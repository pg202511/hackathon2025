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
        assertTrue(result.containsKey("message"), "Result map should contain key 'message'");
        assertEquals("Goodbye, Alice, from REST API for Hackathon 2025!!!!", result.get("message"));
        // Map.of returns an unmodifiable map
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"));
    }

    @Test
    void testGoodbyWithEmptyName() {
        Map<String, String> result = controller.goodby("");
        assertNotNull(result);
        assertEquals("Goodbye, , from REST API for Hackathon 2025!!!!", result.get("message"),
                "Empty name should be reflected in the message (no trimming applied by controller)");
    }

    @Test
    void testGoodbyWithNullName() {
        // When called directly, passing null yields the string "null" in concatenation.
        Map<String, String> result = controller.goodby(null);
        assertNotNull(result);
        assertEquals("Goodbye, null, from REST API for Hackathon 2025!!!!", result.get("message"),
                "When null is passed directly the message will contain the text 'null'");
    }

    @Test
    void testGoodbyWithSpecialCharacters() {
        String special = "Jöhn 🚀, O'Connor";
        Map<String, String> result = controller.goodby(special);
        assertNotNull(result);
        assertEquals("Goodbye, " + special + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodnightDefaultMessage() {
        Map<String, String> result = controller.goodnight();
        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.containsKey("message"));
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
        assertThrows(UnsupportedOperationException.class, () -> result.put("k", "v"));
    }
}