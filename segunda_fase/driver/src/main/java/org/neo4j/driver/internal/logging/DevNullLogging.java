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
package org.neo4j.driver.internal.logging;

import java.io.Serializable;

import org.neo4j.driver.Logger;
import org.neo4j.driver.Logging;

public class DevNullLogging implements Logging, Serializable
{
    private static final long serialVersionUID = -2632752338512373821L;

    public static final Logging DEV_NULL_LOGGING = new DevNullLogging();

    private DevNullLogging()
    {
    }

    @Override
    public Logger getLog( String name )
    {
        return DevNullLogger.DEV_NULL_LOGGER;
    }

    // Don't remove that apparently unused method.
    // It is involved during deserialization after readObject on the new object.
    // The returned value replaces the object read.
    // An enum would be preferable, but would not be API compatible.
    // Reference: https://docs.oracle.com/en/java/javase/17/docs/specs/serialization/input.html#the-readresolve-method andJoshua Bloch, Effective Java 3rd edition
    private Object readResolve()
    {
        return DEV_NULL_LOGGING;
    }
}
