package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    @Test
    void testHelloReturnsNonNullMapWithExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Returned map should contain the 'message' key");

        String message = result.get("message");
        assertNotNull(message, "Message value should not be null");
        assertTrue(message.startsWith("Hello again"), "Message should start with greeting text");
        assertTrue(message.contains("Hackathon 2025"), "Message should mention 'Hackathon 2025'");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", message,
                "Message should exactly match the expected text");
    }

    @Test
    void testHelloMapIsImmutable() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"),
                "Map returned by Map.of(...) should be immutable and throw on put");

        // Also verify remove fails
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"),
                "Map returned by Map.of(...) should be immutable and throw on remove");
    }

    @Test
    void testMultipleCallsReturnEqualContent() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertEquals(first, second, "Subsequent calls should return equivalent maps");
        // They may or may not be the same instance; we only require logical equality and immutability.
        assertTrue(first.containsKey("message") && second.containsKey("message"));
        assertEquals(first.get("message"), second.get("message"));
    }

    @Test
    void testControllerIsAnnotatedWithRestController() {
        boolean annotated = HelloRestController.class.isAnnotationPresent(RestController.class);
        assertTrue(annotated, "HelloRestController should be annotated with @RestController");
    }
}