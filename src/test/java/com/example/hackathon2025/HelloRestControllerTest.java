package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    @Test
    void testHelloReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Map should contain the key 'message'");

        String message = result.get("message");
        assertNotNull(message, "Message value should not be null");
        assertFalse(message.isEmpty(), "Message should not be empty");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", message,
                "Message content should match the expected text");
    }

    @Test
    void testHelloMapIsUnmodifiable() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        // Map.of returns an immutable map; attempting to modify should throw
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"),
                "Attempting to put into the returned map should throw UnsupportedOperationException");

        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"),
                "Attempting to remove from the returned map should throw UnsupportedOperationException");
    }

    @Test
    void testMultipleInvocationsReturnConsistentContent() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertNotNull(first);
        assertNotNull(second);

        // Content should be equal between calls
        assertEquals(first, second, "Consecutive calls should return equal maps with the same content");

        // Both should contain the same expected entry
        assertEquals("Hello again and again from REST API for Hackathon 2025!", first.get("message"));
        assertEquals("Hello again and again from REST API for Hackathon 2025!", second.get("message"));
    }
}