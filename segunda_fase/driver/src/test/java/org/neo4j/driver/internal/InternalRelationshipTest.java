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

import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.function.Function;

import org.neo4j.driver.Value;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.junit.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.neo4j.driver.Values.NULL;
import static org.neo4j.driver.Values.value;

class InternalRelationshipTest
{
    @Test
    void extractValuesFromNode()
    {
        // GIVEN
        InternalRelationship relationship = createRelationship();
        Function<Value,Integer> extractor = Value::asInt;

        //WHEN
        Iterable<Integer> values = relationship.values( extractor );

        //THEN
        Iterator<Integer> iterator = values.iterator();
        assertThat( iterator.next(), equalTo( 1 ) );
        assertThat( iterator.next(), equalTo( 2 ) );
        assertFalse( iterator.hasNext() );
    }

    @Test
    void accessUnknownKeyShouldBeNull()
    {
        InternalRelationship relationship = createRelationship();

        assertThat( relationship.get( "k1" ), equalTo( value( 1 ) ) );
        assertThat( relationship.get( "k2" ), equalTo( value( 2 ) ) );
        assertThat( relationship.get( "k3" ), equalTo( NULL ) );
    }

    @Test
    void shouldThrowOnIdWhenNumericIdUnavailable()
    {
        // GIVEN
        InternalRelationship relationship =
                new InternalRelationship( -1, "value", 1, String.valueOf( 1 ), 2, String.valueOf( 2 ), "T", Collections.emptyMap(), false );

        // WHEN & THEN
        IllegalStateException e = assertThrows( IllegalStateException.class, relationship::id );
        assertEquals( InternalEntity.INVALID_ID_ERROR, e.getMessage() );
    }

    @Test
    void shouldThrowOnStartNodeIdWhenNumericIdUnavailable()
    {
        // GIVEN
        InternalRelationship relationship =
                new InternalRelationship( -1, "value", 1, String.valueOf( 1 ), 2, String.valueOf( 2 ), "T", Collections.emptyMap(), false );

        // WHEN & THEN
        IllegalStateException e = assertThrows( IllegalStateException.class, relationship::startNodeId );
        assertEquals( InternalEntity.INVALID_ID_ERROR, e.getMessage() );
    }

    @Test
    void shouldThrowOnEndNodeIdWhenNumericIdUnavailable()
    {
        // GIVEN
        InternalRelationship relationship =
                new InternalRelationship( -1, "value", 1, String.valueOf( 1 ), 2, String.valueOf( 2 ), "T", Collections.emptyMap(), false );

        // WHEN & THEN
        IllegalStateException e = assertThrows( IllegalStateException.class, relationship::endNodeId );
        assertEquals( InternalEntity.INVALID_ID_ERROR, e.getMessage() );
    }

    private InternalRelationship createRelationship()
    {
        Map<String,Value> props = new HashMap<>();
        props.put( "k1", value( 1 ) );
        props.put( "k2", value( 2 ) );

        return new InternalRelationship( 1L, 0L, 1L, "T", props );
    }

}
