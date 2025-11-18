package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private static final String EXPECTED_KEY = "message";
    private static final String EXPECTED_VALUE = "Hello again and again from REST API for Hackathon 2025!";

    @Test
    void testHelloReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey(EXPECTED_KEY), "Returned map should contain the key 'message'");
        assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY), "Returned message value is unexpected");
    }

    @Test
    void testHelloMapIsImmutable() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"),
                "Map returned by hello() should be immutable and throw on put");

        assertThrows(UnsupportedOperationException.class, () -> result.remove(EXPECTED_KEY),
                "Map returned by hello() should be immutable and throw on remove");
    }

    @Test
    void testMultipleCallsReturnConsistentValue() {
        HelloRestController controller = new HelloRestController();

        for (int i = 0; i < 10; i++) {
            Map<String, String> result = controller.hello();
            assertNotNull(result.get(EXPECTED_KEY), "Message value should not be null on call " + i);
            assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY), "Message value should be consistent across calls");
        }
    }

    @Test
    void testConcurrentAccessConsistency() throws InterruptedException, ExecutionException {
        HelloRestController controller = new HelloRestController();
        int threads = 20;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        try {
            List<Callable<String>> tasks = new ArrayList<>();
            for (int i = 0; i < threads; i++) {
                tasks.add(() -> controller.hello().get(EXPECTED_KEY));
            }

            List<java.util.concurrent.Future<String>> futures = executor.invokeAll(tasks);
            for (java.util.concurrent.Future<String> f : futures) {
                assertEquals(EXPECTED_VALUE, f.get(), "Concurrent call returned unexpected message");
            }
        } finally {
            executor.shutdownNow();
        }
    }

    @Test
    void testNoAdditionalKeysAndValueNotEmpty() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        Set<String> keys = result.keySet();
        assertEquals(Set.of(EXPECTED_KEY), keys, "Only the 'message' key should be present");
        String value = result.get(EXPECTED_KEY);
        assertNotNull(value, "Message value should not be null");
        assertFalse(value.isEmpty(), "Message value should not be empty");
        assertTrue(value.contains("Hackathon 2025"), "Message should mention 'Hackathon 2025'");
    }
}