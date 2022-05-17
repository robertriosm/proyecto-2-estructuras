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
package org.neo4j.driver.internal.spi;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import org.neo4j.driver.internal.BoltServerAddress;
import org.neo4j.driver.net.ServerAddress;

public interface ConnectionPool
{
    String CONNECTION_POOL_CLOSED_ERROR_MESSAGE = "Pool closed";

    CompletionStage<Connection> acquire( BoltServerAddress address );

    void retainAll( Set<BoltServerAddress> addressesToRetain );

    int inUseConnections( ServerAddress address );

    int idleConnections( ServerAddress address );

    CompletionStage<Void> close();

    boolean isOpen( BoltServerAddress address );
}
