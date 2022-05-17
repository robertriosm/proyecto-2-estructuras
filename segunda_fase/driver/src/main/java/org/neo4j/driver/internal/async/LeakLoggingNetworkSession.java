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

import org.neo4j.driver.AccessMode;
import org.neo4j.driver.Logging;
import org.neo4j.driver.internal.BookmarksHolder;
import org.neo4j.driver.internal.DatabaseName;
import org.neo4j.driver.internal.retry.RetryLogic;
import org.neo4j.driver.internal.spi.ConnectionProvider;
import org.neo4j.driver.internal.util.Futures;

import static java.lang.System.lineSeparator;

public class LeakLoggingNetworkSession extends NetworkSession
{
    private final String stackTrace;

    public LeakLoggingNetworkSession( ConnectionProvider connectionProvider, RetryLogic retryLogic, DatabaseName databaseName, AccessMode mode,
                                      BookmarksHolder bookmarksHolder, String impersonatedUser, long fetchSize, Logging logging )
    {
        super( connectionProvider, retryLogic, databaseName, mode, bookmarksHolder, impersonatedUser, fetchSize, logging );
        this.stackTrace = captureStackTrace();
    }

    @Override
    protected void finalize() throws Throwable
    {
        logLeakIfNeeded();
        super.finalize();
    }

    private void logLeakIfNeeded()
    {
        Boolean isOpen = Futures.blockingGet( currentConnectionIsOpen() );
        if ( isOpen )
        {
            log.error( "Neo4j Session object leaked, please ensure that your application " +
                       "fully consumes results in Sessions or explicitly calls `close` on Sessions before disposing of the objects.\n" +
                       "Session was create at:\n" + stackTrace, null );
        }
    }
    private static String captureStackTrace()
    {
        StringBuilder result = new StringBuilder();
        StackTraceElement[] elements = Thread.currentThread().getStackTrace();
        for ( StackTraceElement element : elements )
        {
            result.append( "\t" ).append( element ).append( lineSeparator() );
        }
        return result.toString();
    }
}
