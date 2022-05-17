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
package org.neo4j.driver.integration.async;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.ArrayList;
import java.util.concurrent.ExecutionException;

import org.neo4j.driver.async.AsyncSession;
import org.neo4j.driver.util.DatabaseExtension;
import org.neo4j.driver.util.ParallelizableIT;

import static org.neo4j.driver.Values.parameters;
import static org.neo4j.driver.util.TestUtil.assertNoCircularReferences;

@ParallelizableIT
public class AsyncQueryIT
{
    @RegisterExtension
    static final DatabaseExtension neo4j = new DatabaseExtension();

    private AsyncSession session;

    @BeforeEach
    void setUp()
    {
        session = neo4j.driver().asyncSession();
    }

    @AfterEach
    void tearDown()
    {
        session.closeAsync();
    }

    @Test
    void shouldBeAbleToLogSemanticWrongExceptions() throws ExecutionException, InterruptedException
    {
        session.writeTransactionAsync( tx -> Flux.from(
                Mono.fromCompletionStage(
                        tx.runAsync( "MATCH (n:Element) WHERE n.name = {param} RETURN n", parameters("param", "Luke") )
                )).collectList().toFuture())

               .toCompletableFuture()
               .exceptionally( ex -> {
                   assertNoCircularReferences(ex);
                   return new ArrayList<>();
               } )
               .get();
    }

}
