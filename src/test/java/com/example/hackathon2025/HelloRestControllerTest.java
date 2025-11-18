package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class HelloRestControllerTest {

    private HelloRestController controller;

    @BeforeEach
    public void setUp() {
        controller = new HelloRestController();
    }

    @Test
    public void hello_returnsExpectedMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Returned map should contain the key 'message'");

        String expected = "Hello again and again from REST API for Hackathon 2025!";
        assertEquals(expected, result.get("message"), "The message value should match the expected text");
    }

    @Test
    public void hello_mapEntriesAreNonNull() {
        Map<String, String> result = controller.hello();

        // ensure no null keys or values
        result.forEach((k, v) -> {
            assertNotNull(k, "Key should not be null");
            assertNotNull(v, "Value should not be null");
        });
    }

    @Test
    public void hello_mapIsUnmodifiable() {
        Map<String, String> result = controller.hello();

        // Map.of returns an immutable map — attempts to modify should throw UnsupportedOperationException
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"));
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"));
        assertThrows(UnsupportedOperationException.class, () -> result.clear());
    }

    @Test
    public void hello_multipleInvocationsReturnConsistentContent() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        // Content should be equal across invocations
        assertEquals(first, second, "Subsequent invocations should return equal maps with same content");

        // Verify the single expected mapping is present
        assertEquals(1, second.size());
        assertEquals("Hello again and again from REST API for Hackathon 2025!", second.get("message"));
    }
}