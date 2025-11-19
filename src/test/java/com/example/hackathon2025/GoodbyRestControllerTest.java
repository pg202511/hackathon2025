package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class GoodbyRestControllerTest {

    private final GoodbyRestController controller = new GoodbyRestController();

    @Test
    void goodby_withName_returnsGreeting() {
        Map<String, String> result = controller.goodby("Alice");

        assertNotNull(result, "Resulting map should not be null");
        assertEquals(1, result.size(), "Resulting map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Resulting map should contain 'message' key");
        assertEquals("Goodbye, Alice, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void goodby_withEmptyName_returnsGreetingContainingCommaSpacing() {
        Map<String, String> result = controller.goodby("");

        assertNotNull(result);
        assertEquals("Goodbye, , from REST API for Hackathon 2025!!!!", result.get("message"),
                "Empty name should be inserted as empty string between commas");
    }

    @Test
    void goodby_withNullName_insertsLiteralNull() {
        // Note: When calling the controller method directly, Spring's @RequestParam defaultValue is not applied.
        // This test verifies the direct-call behavior with a null parameter.
        Map<String, String> result = controller.goodby(null);

        assertNotNull(result);
        assertEquals("Goodbye, null, from REST API for Hackathon 2025!!!!", result.get("message"),
                "Direct invocation with null should include the literal 'null' in the message");
    }

    @Test
    void goodby_withSpecialCharacters_preservesThemInMessage() {
        String special = "O'Conner & Co <script> 🚀";
        Map<String, String> result = controller.goodby(special);

        assertNotNull(result);
        assertEquals("Goodbye, " + special + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void goodby_withVeryLongName_includesFullName() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1000; i++) {
            sb.append('x');
        }
        String longName = sb.toString();

        Map<String, String> result = controller.goodby(longName);

        assertNotNull(result);
        assertEquals("Goodbye, " + longName + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void goodby_returnedMapIsUnmodifiable() {
        Map<String, String> result = controller.goodby("Bob");

        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "value"),
                "Map.of returns an unmodifiable map; modification should throw");
    }

    @Test
    void goodnight_returnsExpectedMessageAndMapIsUnmodifiable() {
        Map<String, String> result = controller.goodnight();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
        assertThrows(UnsupportedOperationException.class, () -> result.put("k", "v"),
                "Map.of returns an unmodifiable map; modification should throw");
    }
}