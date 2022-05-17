/*
 * Copyright (c) "Neo4j"
 * Neo4j Sweden AB [http://neo4j.com]
 *
 * This file is part of Neo4j.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.neo4j.driver.internal.cluster;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.ArgumentCaptor;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.neo4j.driver.Logger;
import org.neo4j.driver.Logging;
import org.neo4j.driver.exceptions.AuthenticationException;
import org.neo4j.driver.exceptions.AuthorizationExpiredException;
import org.neo4j.driver.exceptions.ClientException;
import org.neo4j.driver.exceptions.DiscoveryException;
import org.neo4j.driver.exceptions.ProtocolException;
import org.neo4j.driver.exceptions.ServiceUnavailableException;
import org.neo4j.driver.exceptions.SessionExpiredException;
import org.neo4j.driver.internal.BoltServerAddress;
import org.neo4j.driver.internal.DatabaseName;
import org.neo4j.driver.internal.DefaultDomainNameResolver;
import org.neo4j.driver.internal.DomainNameResolver;
import org.neo4j.driver.internal.spi.Connection;
import org.neo4j.driver.internal.spi.ConnectionPool;
import org.neo4j.driver.internal.util.FakeClock;
import org.neo4j.driver.internal.util.ImmediateSchedulingEventExecutor;
import org.neo4j.driver.net.ServerAddressResolver;

import static java.util.Collections.emptySet;
import static java.util.Collections.singletonMap;
import static java.util.concurrent.CompletableFuture.completedFuture;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.startsWith;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.neo4j.driver.internal.DatabaseNameUtil.defaultDatabase;
import static org.neo4j.driver.internal.logging.DevNullLogging.DEV_NULL_LOGGING;
import static org.neo4j.driver.internal.util.ClusterCompositionUtil.A;
import static org.neo4j.driver.internal.util.ClusterCompositionUtil.B;
import static org.neo4j.driver.internal.util.ClusterCompositionUtil.C;
import static org.neo4j.driver.internal.util.ClusterCompositionUtil.D;
import static org.neo4j.driver.internal.util.ClusterCompositionUtil.E;
import static org.neo4j.driver.internal.util.Futures.failedFuture;
import static org.neo4j.driver.util.TestUtil.asOrderedSet;
import static org.neo4j.driver.util.TestUtil.await;

class RediscoveryTest
{
    private final ConnectionPool pool = asyncConnectionPoolMock();

    @Test
    void shouldUseFirstRouterInTable()
    {
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( B, C ), asOrderedSet( C, D ), asOrderedSet( B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( B, expectedComposition ); // first -> valid cluster composition

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( B );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table, never() ).forget( B );
    }

    @Test
    void shouldSkipFailingRouters()
    {
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( A, B, C ), asOrderedSet( B, C, D ), asOrderedSet( A, B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( A, new RuntimeException( "Hi!" ) ); // first -> non-fatal failure
        responsesByAddress.put( B, new ServiceUnavailableException( "Hi!" ) ); // second -> non-fatal failure
        responsesByAddress.put( C, expectedComposition ); // third -> valid cluster composition

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table ).forget( A );
        verify( table ).forget( B );
        verify( table, never() ).forget( C );
    }

    @Test
    void shouldFailImmediatelyOnAuthError()
    {
        AuthenticationException authError = new AuthenticationException( "Neo.ClientError.Security.Unauthorized",
                "Wrong password" );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( A, new RuntimeException( "Hi!" ) ); // first router -> non-fatal failure
        responsesByAddress.put( B, authError ); // second router -> fatal auth error

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        AuthenticationException error = assertThrows( AuthenticationException.class,
                                                      () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertEquals( authError, error );
        verify( table ).forget( A );
    }

    @Test
    void shouldUseAnotherRouterOnAuthorizationExpiredException()
    {
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( A, B, C ), asOrderedSet( B, C, D ), asOrderedSet( A, B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( A, new AuthorizationExpiredException( "Neo.ClientError.Security.AuthorizationExpired", "message" ) );
        responsesByAddress.put( B, expectedComposition );

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table ).forget( A );
        verify( table, never() ).forget( B );
        verify( table, never() ).forget( C );
    }

    @ParameterizedTest
    @ValueSource( strings = {"Neo.ClientError.Transaction.InvalidBookmark", "Neo.ClientError.Transaction.InvalidBookmarkMixture"} )
    void shouldFailImmediatelyOnBookmarkErrors( String code )
    {
        ClientException error = new ClientException( code, "Invalid" );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( A, new RuntimeException( "Hi!" ) );
        responsesByAddress.put( B, error );

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        ClientException actualError = assertThrows( ClientException.class,
                                                    () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertEquals( error, actualError );
        verify( table ).forget( A );
    }

    @Test
    void shouldFailImmediatelyOnClosedPoolError()
    {
        IllegalStateException error = new IllegalStateException( ConnectionPool.CONNECTION_POOL_CLOSED_ERROR_MESSAGE );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( A, new RuntimeException( "Hi!" ) );
        responsesByAddress.put( B, error );

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        IllegalStateException actualError = assertThrows( IllegalStateException.class,
                                                          () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertEquals( error, actualError );
        verify( table ).forget( A );
    }

    @Test
    void shouldFallbackToInitialRouterWhenKnownRoutersFail()
    {
        BoltServerAddress initialRouter = A;
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( C, B, A ), asOrderedSet( A, B ), asOrderedSet( D, E ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( B, new ServiceUnavailableException( "Hi!" ) ); // first -> non-fatal failure
        responsesByAddress.put( C, new ServiceUnavailableException( "Hi!" ) ); // second -> non-fatal failure
        responsesByAddress.put( initialRouter, expectedComposition ); // initial -> valid response

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        ServerAddressResolver resolver = resolverMock( initialRouter, initialRouter );
        Rediscovery rediscovery = newRediscovery( initialRouter, compositionProvider, resolver );
        RoutingTable table = routingTableMock( B, C );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table ).forget( B );
        verify( table ).forget( C );
    }

    @Test
    void shouldFailImmediatelyWhenClusterCompositionProviderReturnsFailure()
    {
        ClusterComposition validComposition =
                new ClusterComposition( 42, asOrderedSet( A ), asOrderedSet( B ), asOrderedSet( C ), null );
        ProtocolException protocolError = new ProtocolException( "Wrong record!" );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( B, protocolError ); // first -> fatal failure
        responsesByAddress.put( C, validComposition ); // second -> valid cluster composition

        Logging logging = mock( Logging.class );
        Logger logger = mock( Logger.class );
        when( logging.getLog( any( Class.class ) ) ).thenReturn( logger );

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ), logging );
        RoutingTable table = routingTableMock( B, C );

        // When
        ClusterComposition composition = await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();
        assertEquals( validComposition, composition );

        ArgumentCaptor<String> warningMessageCaptor = ArgumentCaptor.forClass( String.class );
        ArgumentCaptor<String> debugMessageCaptor = ArgumentCaptor.forClass( String.class );
        ArgumentCaptor<DiscoveryException> debugThrowableCaptor = ArgumentCaptor.forClass( DiscoveryException.class );
        verify( logging ).getLog( RediscoveryImpl.class );
        verify( logger ).warn( warningMessageCaptor.capture() );
        verify( logger ).debug( debugMessageCaptor.capture(), debugThrowableCaptor.capture() );
        assertNotNull( warningMessageCaptor.getValue() );
        assertEquals( warningMessageCaptor.getValue(), debugMessageCaptor.getValue() );
        assertThat( debugThrowableCaptor.getValue().getCause(), equalTo( protocolError ) );
    }

    @Test
    void shouldResolveInitialRouterAddress()
    {
        BoltServerAddress initialRouter = A;
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( A, B ), asOrderedSet( A, B ), asOrderedSet( A, B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( B, new ServiceUnavailableException( "Hi!" ) ); // first -> non-fatal failure
        responsesByAddress.put( C, new ServiceUnavailableException( "Hi!" ) ); // second -> non-fatal failure
        responsesByAddress.put( D, new IOException( "Hi!" ) ); // resolved first -> non-fatal failure
        responsesByAddress.put( E, expectedComposition ); // resolved second -> valid response

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        // initial router resolved to two other addresses
        ServerAddressResolver resolver = resolverMock( initialRouter, D, E );
        Rediscovery rediscovery = newRediscovery( initialRouter, compositionProvider, resolver );
        RoutingTable table = routingTableMock( B, C );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table ).forget( B );
        verify( table ).forget( C );
        verify( table ).forget( D );
    }

    @Test
    void shouldResolveInitialRouterAddressUsingCustomResolver()
    {
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( A, B, C ), asOrderedSet( A, B, C ), asOrderedSet( B, E ), null );

        ServerAddressResolver resolver = address ->
        {
            assertEquals( A, address );
            return asOrderedSet( B, C, E );
        };

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( B, new ServiceUnavailableException( "Hi!" ) ); // first -> non-fatal failure
        responsesByAddress.put( C, new ServiceUnavailableException( "Hi!" ) ); // second -> non-fatal failure
        responsesByAddress.put( E, expectedComposition ); // resolved second -> valid response

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, resolver );
        RoutingTable table = routingTableMock( B, C );

        ClusterComposition actualComposition =
                await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();

        assertEquals( expectedComposition, actualComposition );
        verify( table ).forget( B );
        verify( table ).forget( C );
    }

    @Test
    void shouldPropagateFailureWhenResolverFails()
    {
        ClusterComposition expectedComposition =
                new ClusterComposition( 42, asOrderedSet( A, B ), asOrderedSet( A, B ), asOrderedSet( A, B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = singletonMap( A, expectedComposition );
        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );

        // failing server address resolver
        ServerAddressResolver resolver = mock( ServerAddressResolver.class );
        when( resolver.resolve( A ) ).thenThrow( new RuntimeException( "Resolver fails!" ) );

        Rediscovery rediscovery = newRediscovery( A, compositionProvider, resolver );
        RoutingTable table = routingTableMock();

        RuntimeException error =
                assertThrows( RuntimeException.class, () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertEquals( "Resolver fails!", error.getMessage() );

        verify( resolver ).resolve( A );
        verify( table, never() ).forget( any() );
    }

    @Test
    void shouldRecordAllErrorsWhenNoRouterRespond()
    {
        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        ServiceUnavailableException first = new ServiceUnavailableException( "Hi!" );
        responsesByAddress.put( A, first ); // first -> non-fatal failure
        SessionExpiredException second = new SessionExpiredException( "Hi!" );
        responsesByAddress.put( B, second ); // second -> non-fatal failure
        IOException third = new IOException( "Hi!" );
        responsesByAddress.put( C, third ); // third -> non-fatal failure

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        Rediscovery rediscovery = newRediscovery( A, compositionProvider, mock( ServerAddressResolver.class ) );
        RoutingTable table = routingTableMock( A, B, C );

        ServiceUnavailableException e =
                assertThrows( ServiceUnavailableException.class,
                              () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertThat( e.getMessage(), containsString( "Could not perform discovery" ) );
        assertThat( e.getSuppressed().length, equalTo( 3 ) );
        assertThat( e.getSuppressed()[0].getCause(), equalTo( first ) );
        assertThat( e.getSuppressed()[1].getCause(), equalTo( second ) );
        assertThat( e.getSuppressed()[2].getCause(), equalTo( third ) );
    }

    @Test
    void shouldUseInitialRouterAfterDiscoveryReturnsNoWriters()
    {
        BoltServerAddress initialRouter = A;
        ClusterComposition noWritersComposition =
                new ClusterComposition( 42, asOrderedSet( D, E ), emptySet(), asOrderedSet( D, E ), null );
        ClusterComposition validComposition =
                new ClusterComposition( 42, asOrderedSet( B, A ), asOrderedSet( B, A ), asOrderedSet( B, A ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( initialRouter, validComposition ); // initial -> valid composition

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        ServerAddressResolver resolver = resolverMock( initialRouter, initialRouter );
        Rediscovery rediscovery = newRediscovery( initialRouter, compositionProvider, resolver );
        RoutingTable table = new ClusterRoutingTable( defaultDatabase(), new FakeClock() );
        table.update( noWritersComposition );

        ClusterComposition composition2 = await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();
        assertEquals( validComposition, composition2 );
    }

    @Test
    void shouldUseInitialRouterToStartWith()
    {
        BoltServerAddress initialRouter = A;
        ClusterComposition validComposition =
                new ClusterComposition( 42, asOrderedSet( A ), asOrderedSet( A ), asOrderedSet( A ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( initialRouter, validComposition ); // initial -> valid composition

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        ServerAddressResolver resolver = resolverMock( initialRouter, initialRouter );
        Rediscovery rediscovery = newRediscovery( initialRouter, compositionProvider, resolver );
        RoutingTable table = routingTableMock( true, B, C, D );

        ClusterComposition composition = await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();
        assertEquals( validComposition, composition );
    }

    @Test
    void shouldUseKnownRoutersWhenInitialRouterFails()
    {
        BoltServerAddress initialRouter = A;
        ClusterComposition validComposition =
                new ClusterComposition( 42, asOrderedSet( D, E ), asOrderedSet( E, D ), asOrderedSet( A, B ), null );

        Map<BoltServerAddress,Object> responsesByAddress = new HashMap<>();
        responsesByAddress.put( initialRouter, new ServiceUnavailableException( "Hi" ) ); // initial -> non-fatal error
        responsesByAddress.put( D, new IOException( "Hi" ) ); // first known -> non-fatal failure
        responsesByAddress.put( E, validComposition ); // second known -> valid composition

        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        ServerAddressResolver resolver = resolverMock( initialRouter, initialRouter );
        Rediscovery rediscovery = newRediscovery( initialRouter, compositionProvider, resolver );
        RoutingTable table = routingTableMock( true, D, E );

        ClusterComposition composition = await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ).getClusterComposition();
        assertEquals( validComposition, composition );
        verify( table ).forget( initialRouter );
        verify( table ).forget( D );
    }

    @Test
    void shouldNotLogWhenSingleRetryAttemptFails()
    {
        Map<BoltServerAddress,Object> responsesByAddress = singletonMap( A, new ServiceUnavailableException( "Hi!" ) );
        ClusterCompositionProvider compositionProvider = compositionProviderMock( responsesByAddress );
        ServerAddressResolver resolver = resolverMock( A, A );

        ImmediateSchedulingEventExecutor eventExecutor = new ImmediateSchedulingEventExecutor();
        Logging logging = mock( Logging.class );
        Logger logger = mock( Logger.class );
        when( logging.getLog( any( Class.class ) ) ).thenReturn( logger );
        Rediscovery rediscovery =
                new RediscoveryImpl( A, compositionProvider, resolver, logging, DefaultDomainNameResolver.getInstance() );
        RoutingTable table = routingTableMock( A );

        ServiceUnavailableException e =
                assertThrows( ServiceUnavailableException.class,
                              () -> await( rediscovery.lookupClusterComposition( table, pool, Collections.emptySet(), null ) ) );
        assertThat( e.getMessage(), containsString( "Could not perform discovery" ) );

        // rediscovery should not log about retries and should not schedule any retries
        verify( logging ).getLog( RediscoveryImpl.class );
        verify( logger, never() ).info( startsWith( "Unable to fetch new routing table, will try again in " ) );
        assertEquals( 0, eventExecutor.scheduleDelays().size() );
    }

    @Test
    void shouldResolveToIP() throws UnknownHostException
    {
        ServerAddressResolver resolver = resolverMock( A, A );
        DomainNameResolver domainNameResolver = mock( DomainNameResolver.class );
        InetAddress localhost = InetAddress.getLocalHost();
        when( domainNameResolver.resolve( A.host() ) ).thenReturn( new InetAddress[]{localhost} );
        Rediscovery rediscovery = new RediscoveryImpl( A, null, resolver, DEV_NULL_LOGGING, domainNameResolver );

        List<BoltServerAddress> addresses = rediscovery.resolve();

        verify( resolver, times( 1 ) ).resolve( A );
        verify( domainNameResolver, times( 1 ) ).resolve( A.host() );
        assertEquals( 1, addresses.size() );
        assertEquals( new BoltServerAddress( A.host(), localhost.getHostAddress(), A.port() ), addresses.get( 0 ) );
    }

    private Rediscovery newRediscovery( BoltServerAddress initialRouter, ClusterCompositionProvider compositionProvider,
                                        ServerAddressResolver resolver )
    {
        return newRediscovery( initialRouter, compositionProvider, resolver, DEV_NULL_LOGGING );
    }

    private Rediscovery newRediscovery( BoltServerAddress initialRouter, ClusterCompositionProvider compositionProvider,
                                        ServerAddressResolver resolver, Logging logging )
    {
        return new RediscoveryImpl( initialRouter, compositionProvider, resolver, logging,
                                    DefaultDomainNameResolver.getInstance() );
    }

    @SuppressWarnings( "unchecked" )
    private static ClusterCompositionProvider compositionProviderMock(
            Map<BoltServerAddress,Object> responsesByAddress )
    {
        ClusterCompositionProvider provider = mock( ClusterCompositionProvider.class );
        when( provider.getClusterComposition( any( Connection.class ), any( DatabaseName.class ), any( Set.class ), any() ) )
                .then( invocation ->
                       {
                           Connection connection = invocation.getArgument( 0 );
                           BoltServerAddress address = connection.serverAddress();
                           Object response = responsesByAddress.get( address );
                           assertNotNull( response );
                           if ( response instanceof Throwable )
                           {
                               return failedFuture( (Throwable) response );
                           }
                           else
                           {
                               return completedFuture( response );
                           }
                       } );
        return provider;
    }

    private static ServerAddressResolver resolverMock( BoltServerAddress address, BoltServerAddress... resolved )
    {
        ServerAddressResolver resolver = mock( ServerAddressResolver.class );
        when( resolver.resolve( address ) ).thenReturn( asOrderedSet( resolved ) );
        return resolver;
    }

    private static ConnectionPool asyncConnectionPoolMock()
    {
        ConnectionPool pool = mock( ConnectionPool.class );
        when( pool.acquire( any() ) ).then( invocation ->
        {
            BoltServerAddress address = invocation.getArgument( 0 );
            return completedFuture( asyncConnectionMock( address ) );
        } );
        return pool;
    }

    private static Connection asyncConnectionMock( BoltServerAddress address )
    {
        Connection connection = mock( Connection.class );
        when( connection.serverAddress() ).thenReturn( address );
        return connection;
    }

    private static RoutingTable routingTableMock( BoltServerAddress... routers )
    {
        return routingTableMock( false, routers );
    }

    private static RoutingTable routingTableMock( boolean preferInitialRouter, BoltServerAddress... routers )
    {
        RoutingTable routingTable = mock( RoutingTable.class );
        when( routingTable.routers() ).thenReturn( Arrays.asList( routers ) );
        when( routingTable.database() ).thenReturn( defaultDatabase() );
        when( routingTable.preferInitialRouter() ).thenReturn( preferInitialRouter );
        return routingTable;
    }
}
