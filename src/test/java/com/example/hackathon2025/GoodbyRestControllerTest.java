package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class GoodbyRestControllerTest {

    private GoodbyRestController controller;

    @BeforeEach
    void setUp() {
        controller = new GoodbyRestController();
    }

    @Test
    void testGoodby_withNormalName_returnsExpectedMessage() {
        Map<String, String> result = controller.goodby("Alice");

        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Result map should contain 'message' key");

        String expected = "Goodbye, Alice, from REST API for Hackathon 2025!!!!";
        assertEquals(expected, result.get("message"));
    }

    @Test
    void testGoodby_withEmptyName_includesEmptyPlaceholder() {
        Map<String, String> result = controller.goodby("");

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Goodbye, , from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withNullName_includesNullString() {
        // Although in runtime Spring would supply default value "Gast", calling the method directly with null
        // should produce a message containing the string "null"
        Map<String, String> result = controller.goodby(null);

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Goodbye, null, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withLongName_handlesLargeInput() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1000; i++) {
            sb.append('x');
        }
        String longName = sb.toString();

        Map<String, String> result = controller.goodby(longName);

        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.get("message").contains(longName));
        assertEquals("Goodbye, " + longName + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withSpecialCharacters_preservesInput() {
        String special = "<script>alert('x')</script>";
        Map<String, String> result = controller.goodby(special);

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Goodbye, " + special + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodnight_returnsExpectedFixedMessage() {
        Map<String, String> result = controller.goodnight();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.containsKey("message"));
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
    }

    @Test
    void testReturnedMapsAreUnmodifiable() {
        Map<String, String> goodbyMap = controller.goodby("Bob");
        Map<String, String> goodnightMap = controller.goodnight();

        assertThrows(UnsupportedOperationException.class, () -> goodbyMap.put("another", "value"));
        assertThrows(UnsupportedOperationException.class, () -> goodnightMap.put("another", "value"));

        // original entries remain intact
        assertEquals("Goodbye, Bob, from REST API for Hackathon 2025!!!!", goodbyMap.get("message"));
        assertEquals("Good night from REST API for Hackathon 2025!!!", goodnightMap.get("message"));
    }
}