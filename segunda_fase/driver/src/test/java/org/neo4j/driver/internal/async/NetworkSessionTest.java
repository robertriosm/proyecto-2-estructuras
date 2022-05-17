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
package org.neo4j.driver.internal.async;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;

import java.util.Collections;
import java.util.Set;

import org.neo4j.driver.AccessMode;
import org.neo4j.driver.Bookmark;
import org.neo4j.driver.Query;
import org.neo4j.driver.TransactionConfig;
import org.neo4j.driver.async.ResultCursor;
import org.neo4j.driver.exceptions.ClientException;
import org.neo4j.driver.internal.InternalBookmark;
import org.neo4j.driver.internal.messaging.BoltProtocol;
import org.neo4j.driver.internal.messaging.request.PullMessage;
import org.neo4j.driver.internal.messaging.request.RunWithMetadataMessage;
import org.neo4j.driver.internal.messaging.v4.BoltProtocolV4;
import org.neo4j.driver.internal.spi.Connection;
import org.neo4j.driver.internal.spi.ConnectionProvider;

import static java.util.concurrent.CompletableFuture.completedFuture;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.instanceOf;
import static org.hamcrest.junit.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.neo4j.driver.AccessMode.READ;
import static org.neo4j.driver.AccessMode.WRITE;
import static org.neo4j.driver.internal.util.Futures.failedFuture;
import static org.neo4j.driver.util.TestUtil.await;
import static org.neo4j.driver.util.TestUtil.connectionMock;
import static org.neo4j.driver.util.TestUtil.newSession;
import static org.neo4j.driver.util.TestUtil.setupFailingBegin;
import static org.neo4j.driver.util.TestUtil.setupSuccessfulRunAndPull;
import static org.neo4j.driver.util.TestUtil.setupSuccessfulRunRx;
import static org.neo4j.driver.util.TestUtil.verifyBeginTx;
import static org.neo4j.driver.util.TestUtil.verifyRollbackTx;
import static org.neo4j.driver.util.TestUtil.verifyRunAndPull;
import static org.neo4j.driver.util.TestUtil.verifyRunRx;

class NetworkSessionTest
{
    private Connection connection;
    private ConnectionProvider connectionProvider;
    private NetworkSession session;

    @BeforeEach
    void setUp()
    {
        connection = connectionMock( BoltProtocolV4.INSTANCE );
        connectionProvider = mock( ConnectionProvider.class );
        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) )
                .thenReturn( completedFuture( connection ) );
        session = newSession( connectionProvider );
    }

    @Test
    void shouldFlushOnRunAsync()
    {
        setupSuccessfulRunAndPull( connection );
        await( session.runAsync( new Query( "RETURN 1" ), TransactionConfig.empty() ) );

        verifyRunAndPull( connection, "RETURN 1" );
    }

    @Test
    void shouldFlushOnRunRx()
    {
        setupSuccessfulRunRx( connection );
        await( session.runRx( new Query( "RETURN 1" ), TransactionConfig.empty() ) );

        verifyRunRx( connection, "RETURN 1" );
    }

    @Test
    void shouldNotAllowNewTxWhileOneIsRunning()
    {
        // Given
        beginTransaction( session );

        // Expect
        assertThrows( ClientException.class, () -> beginTransaction( session ) );
    }

    @Test
    void shouldBeAbleToOpenTxAfterPreviousIsClosed()
    {
        // Given
        await( beginTransaction( session ).closeAsync() );

        // When
        UnmanagedTransaction tx = beginTransaction( session );

        // Then we should've gotten a transaction object back
        assertNotNull( tx );
        verifyRollbackTx( connection );
    }

    @Test
    void shouldNotBeAbleToUseSessionWhileOngoingTransaction()
    {
        // Given
        beginTransaction( session );

        // Expect
        assertThrows( ClientException.class, () -> run( session, "RETURN 1" ) );
    }

    @Test
    void shouldBeAbleToUseSessionAgainWhenTransactionIsClosed()
    {
        // Given
        await( beginTransaction( session ).closeAsync() );
        String query = "RETURN 1";
        setupSuccessfulRunAndPull( connection, query );

        // When
        run( session, query );

        // Then
        verifyRunAndPull( connection, query );
    }

    @Test
    void shouldNotCloseAlreadyClosedSession()
    {
        beginTransaction( session );

        close( session );
        close( session );
        close( session );

        verifyRollbackTx( connection );
    }

    @Test
    void runThrowsWhenSessionIsClosed()
    {
        close( session );

        Exception e = assertThrows( Exception.class, () -> run( session, "CREATE ()" ) );
        assertThat( e, instanceOf( ClientException.class ) );
        assertThat( e.getMessage(), containsString( "session is already closed" ) );
    }

    @Test
    void acquiresNewConnectionForRun()
    {
        String query = "RETURN 1";
        setupSuccessfulRunAndPull( connection, query );

        run( session, query );

        verify( connectionProvider ).acquireConnection( any( ConnectionContext.class ) );
    }

    @Test
    void releasesOpenConnectionUsedForRunWhenSessionIsClosed()
    {
        String query = "RETURN 1";
        setupSuccessfulRunAndPull( connection, query );

        run( session, query );

        close( session );

        InOrder inOrder = inOrder( connection );
        inOrder.verify( connection ).write( any( RunWithMetadataMessage.class ), any() );
        inOrder.verify( connection ).writeAndFlush( any( PullMessage.class ), any() );
        inOrder.verify( connection, atLeastOnce() ).release();
    }

    @Test
    void closeWithoutConnection()
    {
        NetworkSession session = newSession( connectionProvider );

        close( session );

        verify( connectionProvider, never() ).acquireConnection( any( ConnectionContext.class ) );
    }

    @Test
    void acquiresNewConnectionForBeginTx()
    {
        UnmanagedTransaction tx = beginTransaction( session );

        assertNotNull( tx );
        verify( connectionProvider ).acquireConnection( any( ConnectionContext.class ) );
    }

    @Test
    void updatesBookmarkWhenTxIsClosed()
    {
        Bookmark bookmarkAfterCommit = InternalBookmark.parse( "TheBookmark" );

        BoltProtocol protocol = spy( BoltProtocolV4.INSTANCE );
        doReturn( completedFuture( bookmarkAfterCommit ) ).when( protocol ).commitTransaction( any( Connection.class ) );

        when( connection.protocol() ).thenReturn( protocol );

        UnmanagedTransaction tx = beginTransaction( session );
        assertThat( session.lastBookmarks(), instanceOf( Set.class ) );
        Set<Bookmark> bookmarks = session.lastBookmarks();
        assertTrue( bookmarks.isEmpty() );

        await( tx.commitAsync() );
        assertEquals( Collections.singleton( bookmarkAfterCommit ), session.lastBookmarks() );
    }

    @Test
    void releasesConnectionWhenTxIsClosed()
    {
        String query = "RETURN 42";
        setupSuccessfulRunAndPull( connection, query );

        UnmanagedTransaction tx = beginTransaction( session );
        await( tx.runAsync( new Query( query ) ) );

        verify( connectionProvider ).acquireConnection( any( ConnectionContext.class ) );
        verifyRunAndPull( connection, query );

        await( tx.closeAsync() );
        verify( connection ).release();
    }

    @Test
    void bookmarkIsPropagatedFromSession()
    {
        Set<Bookmark> bookmarks = Collections.singleton( InternalBookmark.parse( "Bookmarks" ) );
        NetworkSession session = newSession( connectionProvider, bookmarks );

        UnmanagedTransaction tx = beginTransaction( session );
        assertNotNull( tx );
        verifyBeginTx( connection );
    }

    @Test
    void bookmarkIsPropagatedBetweenTransactions()
    {
        Bookmark bookmark1 = InternalBookmark.parse( "Bookmark1" );
        Bookmark bookmark2 = InternalBookmark.parse( "Bookmark2" );

        NetworkSession session = newSession( connectionProvider );

        BoltProtocol protocol = spy( BoltProtocolV4.INSTANCE );
        doReturn( completedFuture( bookmark1 ), completedFuture( bookmark2 ) ).when( protocol ).commitTransaction( any( Connection.class ) );

        when( connection.protocol() ).thenReturn( protocol );

        UnmanagedTransaction tx1 = beginTransaction( session );
        await( tx1.commitAsync() );
        assertEquals( Collections.singleton( bookmark1 ), session.lastBookmarks() );

        UnmanagedTransaction tx2 = beginTransaction( session );
        verifyBeginTx( connection, 2 );
        await( tx2.commitAsync() );

        assertEquals( Collections.singleton( bookmark2 ), session.lastBookmarks() );
    }

    @Test
    void accessModeUsedToAcquireReadConnections()
    {
        accessModeUsedToAcquireConnections( READ );
    }

    @Test
    void accessModeUsedToAcquireWriteConnections()
    {
        accessModeUsedToAcquireConnections( WRITE );
    }

    private void accessModeUsedToAcquireConnections( AccessMode mode )
    {
        NetworkSession session2 = newSession( connectionProvider, mode );
        beginTransaction( session2 );
        ArgumentCaptor<ConnectionContext> argument = ArgumentCaptor.forClass( ConnectionContext.class );
        verify( connectionProvider ).acquireConnection( argument.capture() );
        assertEquals( mode, argument.getValue().mode() );
    }

    @Test
    void testPassingNoBookmarkShouldRetainBookmark()
    {
        Set<Bookmark> bookmarks = Collections.singleton( InternalBookmark.parse( "X" ) );
        NetworkSession session = newSession( connectionProvider, bookmarks );
        beginTransaction( session );
        assertThat( session.lastBookmarks(), equalTo( bookmarks ) );
    }

    @Test
    void shouldHaveEmptyLastBookmarksInitially()
    {
        assertTrue( session.lastBookmarks().isEmpty() );
    }

    @Test
    void shouldDoNothingWhenClosingWithoutAcquiredConnection()
    {
        RuntimeException error = new RuntimeException( "Hi" );
        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) ).thenReturn( failedFuture( error ) );

        Exception e = assertThrows( Exception.class, () -> run( session, "RETURN 1" ) );
        assertEquals( error, e );

        close( session );
    }

    @Test
    void shouldRunAfterRunFailure()
    {
        RuntimeException error = new RuntimeException( "Hi" );
        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) )
                .thenReturn( failedFuture( error ) ).thenReturn( completedFuture( connection ) );

        Exception e = assertThrows( Exception.class, () -> run( session, "RETURN 1" ) );

        assertEquals( error, e );

        String query = "RETURN 2";
        setupSuccessfulRunAndPull( connection, query );

        run( session, query );

        verify( connectionProvider, times( 2 ) ).acquireConnection( any( ConnectionContext.class ) );
        verifyRunAndPull( connection, query );
    }

    @Test
    void shouldRunAfterBeginTxFailureOnBookmark()
    {
        RuntimeException error = new RuntimeException( "Hi" );
        Connection connection1 = connectionMock( BoltProtocolV4.INSTANCE );
        setupFailingBegin( connection1, error );
        Connection connection2 = connectionMock( BoltProtocolV4.INSTANCE );

        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) )
                .thenReturn( completedFuture( connection1 ) ).thenReturn( completedFuture( connection2 ) );

        Set<Bookmark> bookmarks = Collections.singleton( InternalBookmark.parse( "neo4j:bookmark:v1:tx42" ) );
        NetworkSession session = newSession( connectionProvider, bookmarks );

        Exception e = assertThrows( Exception.class, () -> beginTransaction( session ) );
        assertEquals( error, e );
        String query = "RETURN 2";
        setupSuccessfulRunAndPull( connection2, query );

        run( session, query );

        verify( connectionProvider, times( 2 ) ).acquireConnection( any( ConnectionContext.class ) );
        verifyBeginTx( connection1 );
        verifyRunAndPull( connection2, "RETURN 2" );
    }

    @Test
    void shouldBeginTxAfterBeginTxFailureOnBookmark()
    {
        RuntimeException error = new RuntimeException( "Hi" );
        Connection connection1 = connectionMock( BoltProtocolV4.INSTANCE );
        setupFailingBegin( connection1, error );
        Connection connection2 = connectionMock( BoltProtocolV4.INSTANCE );

        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) )
                .thenReturn( completedFuture( connection1 ) ).thenReturn( completedFuture( connection2 ) );

        Set<Bookmark> bookmarks = Collections.singleton( InternalBookmark.parse( "neo4j:bookmark:v1:tx42" ) );
        NetworkSession session = newSession( connectionProvider, bookmarks );

        Exception e = assertThrows( Exception.class, () -> beginTransaction( session ) );
        assertEquals( error, e );

        beginTransaction( session );

        verify( connectionProvider, times( 2 ) ).acquireConnection( any( ConnectionContext.class ) );
        verifyBeginTx( connection1 );
        verifyBeginTx( connection2 );
    }

    @Test
    void shouldBeginTxAfterRunFailureToAcquireConnection()
    {
        RuntimeException error = new RuntimeException( "Hi" );
        when( connectionProvider.acquireConnection( any( ConnectionContext.class ) ) )
                .thenReturn( failedFuture( error ) ).thenReturn( completedFuture( connection ) );

        Exception e = assertThrows( Exception.class, () -> run( session, "RETURN 1" ) );
        assertEquals( error, e );

        beginTransaction( session );

        verify( connectionProvider, times( 2 ) ).acquireConnection( any( ConnectionContext.class ) );
        verifyBeginTx( connection );
    }

    private static ResultCursor run(NetworkSession session, String query )
    {
        return await( session.runAsync( new Query( query ), TransactionConfig.empty() ) );
    }

    private static UnmanagedTransaction beginTransaction(NetworkSession session )
    {
        return await( session.beginTransactionAsync( TransactionConfig.empty() ) );
    }

    private static void close( NetworkSession session )
    {
        await( session.closeAsync() );
    }
}
