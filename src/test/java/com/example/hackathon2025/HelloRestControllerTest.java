package com.example.hackathon2025;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.*;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private HelloRestController controller;
    private static final String EXPECTED_MESSAGE = "Hello again and again from REST API for Hackathon 2025!";

    @BeforeEach
    void setUp() {
        controller = new HelloRestController();
    }

    @Test
    void testHelloReturnsNonNullMapWithExpectedContent() {
        Map<String, String> result = controller.hello();
        assertNotNull(result, "Returned map should not be null");
        assertFalse(result.isEmpty(), "Returned map should not be empty");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Returned map must contain the 'message' key");
        String message = result.get("message");
        assertNotNull(message, "'message' value should not be null");
        assertEquals(EXPECTED_MESSAGE, message, "The message content must match the expected text exactly");
        assertTrue(message.contains("REST API"), "Message should mention 'REST API'");
        assertTrue(message.contains("Hackathon 2025"), "Message should mention 'Hackathon 2025'");
    }

    @Test
    void testReturnedMapIsImmutable() {
        Map<String, String> result = controller.hello();
        // Map.of returns an immutable map; mutation should throw
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"),
                "Mutating the returned map should throw UnsupportedOperationException");
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"),
                "Removing from the returned map should throw UnsupportedOperationException");
        assertThrows(UnsupportedOperationException.class, () -> result.clear(),
                "Clearing the returned map should throw UnsupportedOperationException");
    }

    @Test
    void testMultipleCallsReturnConsistentContent() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();
        assertEquals(first, second, "Multiple calls should return equal maps (same content)");
        assertEquals(EXPECTED_MESSAGE, first.get("message"));
        assertEquals(EXPECTED_MESSAGE, second.get("message"));
    }

    @Test
    void testNoNullKeysOrValues() {
        Map<String, String> result = controller.hello();
        for (Map.Entry<String, String> e : result.entrySet()) {
            assertNotNull(e.getKey(), "Map must not contain null keys");
            assertNotNull(e.getValue(), "Map must not contain null values");
        }
    }

    @Test
    void testConcurrentAccessReturnsConsistentResults() throws InterruptedException, ExecutionException, TimeoutException {
        int threads = 20;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        try {
            Callable<Map<String, String>> task = controller::hello;
            List<Future<Map<String, String>>> futures = executor.invokeAll(
                    Collections.nCopies(threads, task), 5, TimeUnit.SECONDS);

            // Collect results and assert consistency
            Map<String, String> expected = controller.hello();
            for (Future<Map<String, String>> f : futures) {
                assertTrue(f.isDone(), "Task should be completed");
                Map<String, String> map = f.get(1, TimeUnit.SECONDS);
                assertEquals(expected, map, "Concurrent call should return the same content as expected");
                // also validate message value individually
                assertEquals(EXPECTED_MESSAGE, map.get("message"));
            }
        } finally {
            executor.shutdownNow();
            if (!executor.awaitTermination(1, TimeUnit.SECONDS)) {
                // best-effort cleanup
            }
        }
    }

    // small utility to provide Collections.nCopies without importing java.util.Collections at top-level
    private static class Collections {
        static <T> List<T> nCopies(int n, T item) {
            return java.util.Collections.nCopies(n, item);
        }
    }
}