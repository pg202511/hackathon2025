package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

import static org.junit.jupiter.api.Assertions.*;

public class HelloRestControllerTest {

    private static final String EXPECTED_MESSAGE = "Hello again and again from REST API for Hackathon 2025!";

    @Test
    public void testHelloReturnsExpectedMap() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> result = controller.hello();

        assertNotNull(result, "Resulting map should not be null");
        assertEquals(1, result.size(), "Map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Map should contain the key 'message'");
        assertEquals(EXPECTED_MESSAGE, result.get("message"), "The message value should match the expected text");
    }

    @Test
    public void testReturnedMapIsImmutable() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        // Map.of returns an immutable map; attempts to modify should throw UnsupportedOperationException
        assertThrows(UnsupportedOperationException.class, () -> {
            result.put("another", "value");
        }, "Modifying the returned map should throw UnsupportedOperationException");
    }

    @Test
    public void testMultipleCallsProduceConsistentResults() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertEquals(first, second, "Multiple calls should produce equal maps");
        assertEquals(EXPECTED_MESSAGE, second.get("message"), "Second call should contain the expected message");
    }

    @Test
    public void testConcurrentAccessIsConsistent() throws InterruptedException, ExecutionException, TimeoutException {
        HelloRestController controller = new HelloRestController();
        int threadCount = 10;
        int tasksPerThread = 20;
        int totalTasks = threadCount * tasksPerThread;

        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        try {
            List<Callable<Map<String, String>>> callables = new ArrayList<>(totalTasks);
            for (int i = 0; i < totalTasks; i++) {
                callables.add(controller::hello);
            }

            List<Future<Map<String, String>>> futures = executor.invokeAll(callables);

            for (Future<Map<String, String>> future : futures) {
                // Use a timeout per future to avoid hanging tests in case of issues
                Map<String, String> result = future.get(2, TimeUnit.SECONDS);
                assertNotNull(result, "Concurrent call should not return null");
                assertEquals(1, result.size(), "Concurrent call map should contain exactly one entry");
                assertEquals(EXPECTED_MESSAGE, result.get("message"), "Concurrent call should return expected message");
            }
        } finally {
            executor.shutdownNow();
            if (!executor.awaitTermination(1, TimeUnit.SECONDS)) {
                // best-effort shutdown; nothing to do
            }
        }
    }
}