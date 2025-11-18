package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private HelloRestController controller;

    @BeforeEach
    void setUp() {
        controller = new HelloRestController();
    }

    @Test
    @DisplayName("hello() returns a non-null map containing the expected message")
    void testHelloReturnsExpectedMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Resulting map should not be null");
        assertFalse(result.isEmpty(), "Resulting map should not be empty");
        assertEquals(1, result.size(), "Resulting map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Resulting map should contain the key 'message'");

        String message = result.get("message");
        assertNotNull(message, "Message value should not be null");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", message,
                "Message content should match the expected greeting");
    }

    @Test
    @DisplayName("hello() returns an immutable map (attempting modification throws UnsupportedOperationException)")
    void testMapIsImmutable() {
        Map<String, String> result = controller.hello();

        // put should throw UnsupportedOperationException for immutable Map.of(...)
        assertThrows(UnsupportedOperationException.class, () -> result.put("newKey", "value"),
                "Putting into the returned map should throw UnsupportedOperationException");

        // remove should also throw
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"),
                "Removing from the returned map should throw UnsupportedOperationException");
    }

    @Test
    @DisplayName("Multiple invocations produce equivalent maps (content equality)")
    void testMultipleInvocationsReturnEqualContent() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        // They may or may not be the same instance, but they must be equal in content
        assertEquals(first, second, "Two invocations should return maps with equal content");
    }

    @Test
    @DisplayName("Returned map contains no null keys or values")
    void testNoNullKeysOrValues() {
        Map<String, String> result = controller.hello();

        // Ensure keys and values are non-null by iterating entries
        result.forEach((k, v) -> {
            assertNotNull(k, "Map should not contain null keys");
            assertNotNull(v, "Map should not contain null values");
        });
    }

    @Test
    @DisplayName("String representation of the map contains the greeting text")
    void testToStringContainsGreeting() {
        Map<String, String> result = controller.hello();
        String repr = result.toString();

        assertTrue(repr.contains("Hackathon 2025") || repr.contains("Hackathon2025"),
                "String representation should contain reference to 'Hackathon 2025'");
    }
}