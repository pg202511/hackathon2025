package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private final HelloRestController controller = new HelloRestController();

    @Test
    void hello_returnsExpectedMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Map should contain exactly one entry");
        assertEquals(Set.of("message"), result.keySet(), "Map should only contain 'message' key");
        String value = result.get("message");
        assertNotNull(value, "Message value should not be null");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", value);

        // Map.of produces an unmodifiable map -> verify immutability
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "x"));
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"));
    }

    @Test
    void hello2_returnsDummyTextAndIsImmutable() {
        Map<String, String> result = controller.hello2();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.containsKey("message"));
        assertEquals("Dummy text for hello2", result.get("message"));
        assertFalse(result.get("message").isEmpty());

        // verify unmodifiable behavior
        assertThrows(UnsupportedOperationException.class, () -> result.put("k", "v"));
    }

    @Test
    void hello3_returnsAnotherDummyTextAndRepeatedCallsAreConsistent() {
        Map<String, String> first = controller.hello3();
        Map<String, String> second = controller.hello3();

        assertNotNull(first);
        assertNotNull(second);

        // Content should be equal across invocations
        assertEquals(first, second);
        assertEquals(1, first.size());
        assertEquals("Another dummy text for hello3", first.get("message"));

        // ensure key set is exactly the expected one
        assertEquals(Set.of("message"), first.keySet());

        // immutability
        assertThrows(UnsupportedOperationException.class, () -> first.put("x", "y"));
    }
}