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
package org.neo4j.driver.internal.handlers;

import java.util.Map;

import org.neo4j.driver.Value;
import org.neo4j.driver.exceptions.AuthorizationExpiredException;
import org.neo4j.driver.exceptions.ConnectionReadTimeoutException;
import org.neo4j.driver.internal.BookmarksHolder;
import org.neo4j.driver.internal.spi.Connection;
import org.neo4j.driver.internal.util.MetadataExtractor;

import static java.util.Objects.requireNonNull;

public class SessionPullResponseCompletionListener implements PullResponseCompletionListener
{
    private final BookmarksHolder bookmarksHolder;
    private final Connection connection;

    public SessionPullResponseCompletionListener( Connection connection, BookmarksHolder bookmarksHolder )
    {
        this.connection = requireNonNull( connection );
        this.bookmarksHolder = requireNonNull( bookmarksHolder );
    }

    @Override
    public void afterSuccess( Map<String,Value> metadata )
    {
        releaseConnection();
        bookmarksHolder.setBookmark( MetadataExtractor.extractBookmarks( metadata ) );
    }

    @Override
    public void afterFailure( Throwable error )
    {
        if ( error instanceof AuthorizationExpiredException )
        {
            connection.terminateAndRelease( AuthorizationExpiredException.DESCRIPTION );
        }
        else if ( error instanceof ConnectionReadTimeoutException )
        {
            connection.terminateAndRelease( error.getMessage() );
        }
        else
        {
            releaseConnection();
        }
    }

    private void releaseConnection()
    {
        connection.release(); // release in background
    }
}
