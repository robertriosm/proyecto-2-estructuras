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
package org.neo4j.driver.internal;

import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * A resolver function used by the driver to resolve domain names.
 */
@FunctionalInterface
public interface DomainNameResolver
{
    /**
     * Resolve the given domain name to a set of addresses.
     *
     * @param name the name to resolve.
     * @return the resolved addresses.
     * @throws UnknownHostException must be thrown if the given name can not be resolved to at least one address.
     */
    InetAddress[] resolve( String name ) throws UnknownHostException;
}
