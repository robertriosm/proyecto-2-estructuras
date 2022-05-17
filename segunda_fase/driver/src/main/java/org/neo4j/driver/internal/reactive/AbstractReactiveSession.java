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
package org.neo4j.driver.internal.reactive;

import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.function.Function;

import org.neo4j.driver.AccessMode;
import org.neo4j.driver.Bookmark;
import org.neo4j.driver.TransactionConfig;
import org.neo4j.driver.exceptions.TransactionNestingException;
import org.neo4j.driver.internal.async.NetworkSession;
import org.neo4j.driver.internal.async.UnmanagedTransaction;
import org.neo4j.driver.internal.util.Futures;

import static org.neo4j.driver.internal.reactive.RxUtils.createEmptyPublisher;
import static org.neo4j.driver.internal.reactive.RxUtils.createSingleItemPublisher;

abstract class AbstractReactiveSession<S>
{
    protected final NetworkSession session;

    public AbstractReactiveSession( NetworkSession session )
    {
        // RxSession accept a network session as input.
        // The network session different from async session that it provides ways to both run for Rx and Async
        // Note: Blocking result could just build on top of async result. However, Rx result cannot just build on top of async result.
        this.session = session;
    }

    abstract S createTransaction( UnmanagedTransaction unmanagedTransaction );

    abstract Publisher<Void> closeTransaction( S transaction, boolean commit );

    public Publisher<S> beginTransaction( TransactionConfig config )
    {
        return createSingleItemPublisher(
                () ->
                {
                    CompletableFuture<S> txFuture = new CompletableFuture<>();
                    session.beginTransactionAsync( config ).whenComplete(
                            ( tx, completionError ) ->
                            {
                                if ( tx != null )
                                {
                                    txFuture.complete( createTransaction( tx ) );
                                }
                                else
                                {
                                    releaseConnectionBeforeReturning( txFuture, completionError );
                                }
                            } );
                    return txFuture;
                }, () -> new IllegalStateException( "Unexpected condition, begin transaction call has completed successfully with transaction being null" ) );
    }

    Publisher<S> beginTransaction( AccessMode mode, TransactionConfig config )
    {
        return createSingleItemPublisher(
                () ->
                {
                    CompletableFuture<S> txFuture = new CompletableFuture<>();
                    session.beginTransactionAsync( mode, config ).whenComplete(
                            ( tx, completionError ) ->
                            {
                                if ( tx != null )
                                {
                                    txFuture.complete( createTransaction( tx ) );
                                }
                                else
                                {
                                    releaseConnectionBeforeReturning( txFuture, completionError );
                                }
                            } );
                    return txFuture;
                }, () -> new IllegalStateException( "Unexpected condition, begin transaction call has completed successfully with transaction being null" ) );
    }

    <T> Publisher<T> runTransaction( AccessMode mode, Function<S,? extends Publisher<T>> work, TransactionConfig config )
    {
        Flux<T> repeatableWork = Flux.usingWhen( beginTransaction( mode, config ),
                                                 work,
                                                 tx -> closeTransaction( tx, true ),
                                                 ( tx, error ) -> closeTransaction( tx, false ),
                                                 ( tx ) -> closeTransaction( tx, false ) );
        return session.retryLogic().retryRx( repeatableWork );
    }

    private <T> void releaseConnectionBeforeReturning( CompletableFuture<T> returnFuture, Throwable completionError )
    {
        // We failed to create a result cursor, so we cannot rely on result cursor to clean-up resources.
        // Therefore, we will first release the connection that might have been created in the session and then notify the error.
        // The logic here shall be the same as `SessionPullResponseHandler#afterFailure`.
        // The reason we need to release connection in session is that we made `rxSession.close()` optional;
        // Otherwise, session.close shall handle everything for us.
        Throwable error = Futures.completionExceptionCause( completionError );
        if ( error instanceof TransactionNestingException )
        {
            returnFuture.completeExceptionally( error );
        }
        else
        {
            session.releaseConnectionAsync().whenComplete( ( ignored, closeError ) ->
                                                                   returnFuture.completeExceptionally( Futures.combineErrors( error, closeError ) ) );
        }
    }

    public Set<Bookmark> lastBookmarks()
    {
        return session.lastBookmarks();
    }

    public <T> Publisher<T> close()
    {
        return createEmptyPublisher( session::closeAsync );
    }
}
