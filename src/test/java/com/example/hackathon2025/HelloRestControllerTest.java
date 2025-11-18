package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private HelloRestController controller;
    private static final String EXPECTED_KEY = "message";
    private static final String EXPECTED_VALUE = "Hello again and again from REST API for Hackathon 2025!";

    @BeforeEach
    void setUp() {
        controller = new HelloRestController();
    }

    @Test
    @DisplayName("hello() returns a non-null map containing the expected key and value")
    void testHelloReturnsExpectedMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should have exactly one entry");
        assertTrue(result.containsKey(EXPECTED_KEY), "Result map should contain the 'message' key");
        assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY), "Message value should match expected text");
    }

    @Test
    @DisplayName("hello() result should be immutable (modification attempts throw UnsupportedOperationException)")
    void testHelloResultIsImmutable() {
        Map<String, String> result = controller.hello();

        // Map.of returns an immutable map; attempts to modify should throw UOE
        assertThrows(UnsupportedOperationException.class, () -> {
            result.put("another", "value");
        }, "Attempting to put into immutable map should throw UnsupportedOperationException");

        assertThrows(UnsupportedOperationException.class, () -> {
            result.clear();
        }, "Attempting to clear immutable map should throw UnsupportedOperationException");
    }

    @Test
    @DisplayName("Multiple calls to hello() are idempotent (return equal maps)")
    void testHelloIdempotentMultipleCalls() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertEquals(first, second, "Subsequent calls to hello() should return equal maps");
        assertEquals(EXPECTED_VALUE, second.get(EXPECTED_KEY), "Value should remain the expected message");
    }

    @Test
    @DisplayName("Concurrent access to hello() returns consistent results without throwing exceptions")
    void testHelloConcurrentAccess() throws InterruptedException, ExecutionException {
        final int threads = 20;
        final int callsPerThread = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threads);

        try {
            Callable<Map<String, String>> task = () -> controller.hello();

            // Submit many tasks concurrently
            Future<Map<String, String>>[] futures = IntStream.range(0, threads * callsPerThread)
                    .mapToObj(i -> executor.submit(task))
                    .toArray(Future[]::new);

            // Ensure all returned maps are non-null and equal to expected
            for (Future<Map<String, String>> f : futures) {
                Map<String, String> map = f.get(); // may throw ExecutionException
                assertNotNull(map, "Concurrent call should not return null");
                assertEquals(EXPECTED_VALUE, map.get(EXPECTED_KEY), "Concurrent call returned unexpected value");
                assertEquals(1, map.size(), "Concurrent call should return a single-entry map");
            }
        } finally {
            executor.shutdownNow();
        }
    }

    @Test
    @DisplayName("Returned map contains no null keys or values")
    void testNoNullKeysOrValues() {
        Map<String, String> result = controller.hello();

        // Validate keys and values are non-null
        result.forEach((k, v) -> {
            assertNotNull(k, "Key should not be null");
            assertNotNull(v, "Value should not be null");
        });

        // Additionally ensure there are no unexpected entries
        assertTrue(result.keySet().stream().allMatch(Objects::nonNull), "All keys must be non-null");
        assertTrue(result.values().stream().allMatch(Objects::nonNull), "All values must be non-null");
    }
}