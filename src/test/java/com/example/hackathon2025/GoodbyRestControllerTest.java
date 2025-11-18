package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class GoodbyRestControllerTest {

    private final GoodbyRestController controller = new GoodbyRestController();

    @Test
    void testGoodbyWithName() {
        Map<String, String> result = controller.goodby("Alice");

        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Result map should contain 'message' key");
        assertEquals("Goodbye, Alice, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodbyWithNullName() {
        // Calling method directly with null simulates a caller bypassing Spring's defaultValue behavior
        Map<String, String> result = controller.goodby(null);

        assertNotNull(result);
        assertEquals("Goodbye, null, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodbyWithEmptyName() {
        Map<String, String> result = controller.goodby("");

        assertNotNull(result);
        assertEquals("Goodbye, , from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodbyMapIsUnmodifiable() {
        Map<String, String> result = controller.goodby("Bob");

        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"));
        // ensure original value remains unchanged
        assertEquals("Goodbye, Bob, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodnightNormal() {
        Map<String, String> result = controller.goodnight();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
    }

    @Test
    void testGoodnightMapIsUnmodifiable() {
        Map<String, String> result = controller.goodnight();

        assertThrows(UnsupportedOperationException.class, () -> result.put("x", "y"));
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
    }

    @Test
    void testGoodbyWithSpecialCharacters() {
        String special = "ÄÖÜ-测试-😀";
        Map<String, String> result = controller.goodby(special);

        assertNotNull(result);
        assertEquals("Goodbye, " + special + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }
}