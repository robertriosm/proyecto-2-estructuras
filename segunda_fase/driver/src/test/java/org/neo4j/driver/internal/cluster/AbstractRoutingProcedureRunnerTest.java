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

import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletionStage;

import org.neo4j.driver.Record;
import org.neo4j.driver.exceptions.ClientException;
import org.neo4j.driver.internal.messaging.BoltProtocol;
import org.neo4j.driver.internal.messaging.BoltProtocolVersion;
import org.neo4j.driver.internal.spi.Connection;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.neo4j.driver.internal.DatabaseNameUtil.defaultDatabase;
import static org.neo4j.driver.internal.util.Futures.completedWithNull;
import static org.neo4j.driver.internal.util.Futures.failedFuture;
import static org.neo4j.driver.util.TestUtil.await;

abstract class AbstractRoutingProcedureRunnerTest
{
    @Test
    void shouldReturnFailedResponseOnClientException()
    {
        ClientException error = new ClientException( "Hi" );
        SingleDatabaseRoutingProcedureRunner runner = singleDatabaseRoutingProcedureRunner( RoutingContext.EMPTY, failedFuture( error ) );

        RoutingProcedureResponse response = await( runner.run( connection(), defaultDatabase(), Collections.emptySet(), null ) );

        assertFalse( response.isSuccess() );
        assertEquals( error, response.error() );
    }

    @Test
    void shouldReturnFailedStageOnError()
    {
        Exception error = new Exception( "Hi" );
        SingleDatabaseRoutingProcedureRunner runner = singleDatabaseRoutingProcedureRunner( RoutingContext.EMPTY, failedFuture( error ) );

        Exception e = assertThrows( Exception.class, () -> await( runner.run( connection(), defaultDatabase(), Collections.emptySet(), null ) ) );
        assertEquals( error, e );
    }

    @Test
    void shouldReleaseConnectionOnSuccess()
    {
        SingleDatabaseRoutingProcedureRunner runner = singleDatabaseRoutingProcedureRunner( RoutingContext.EMPTY );

        Connection connection = connection();
        RoutingProcedureResponse response = await( runner.run( connection, defaultDatabase(), Collections.emptySet(), null ) );

        assertTrue( response.isSuccess() );
        verify( connection ).release();
    }

    @Test
    void shouldPropagateReleaseError()
    {
        SingleDatabaseRoutingProcedureRunner runner = singleDatabaseRoutingProcedureRunner( RoutingContext.EMPTY );

        RuntimeException releaseError = new RuntimeException( "Release failed" );
        Connection connection = connection( failedFuture( releaseError ) );

        RuntimeException e = assertThrows( RuntimeException.class, () -> await( runner.run( connection, defaultDatabase(), Collections.emptySet(), null ) ) );
        assertEquals( releaseError, e );
        verify( connection ).release();
    }

    abstract SingleDatabaseRoutingProcedureRunner singleDatabaseRoutingProcedureRunner( RoutingContext context );

    abstract SingleDatabaseRoutingProcedureRunner singleDatabaseRoutingProcedureRunner( RoutingContext context, CompletionStage<List<Record>> runProcedureResult );

    static Connection connection()
    {
        return connection( completedWithNull() );
    }

    static Connection connection( CompletionStage<Void> releaseStage )
    {
        Connection connection = mock( Connection.class );
        BoltProtocol boltProtocol = mock( BoltProtocol.class );
        BoltProtocolVersion protocolVersion = new BoltProtocolVersion( 4, 4 );
        when( boltProtocol.version() ).thenReturn( protocolVersion );
        when( connection.protocol() ).thenReturn( boltProtocol );
        when( connection.release() ).thenReturn( releaseStage );
        return connection;
    }
}
