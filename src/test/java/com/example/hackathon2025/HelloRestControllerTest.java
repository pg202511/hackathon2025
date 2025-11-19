package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    @Test
    void testHello_returnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> result = controller.hello();

        assertNotNull(result, "Resulting map should not be null");
        assertEquals(1, result.size(), "Map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Map should contain 'message' key");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", result.get("message"));
        assertEquals(Set.of("message"), result.keySet(), "Only 'message' key expected");
    }

    @Test
    void testHello2_returnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> result = controller.hello2();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Dummy text for hello2", result.get("message"));
    }

    @Test
    void testHello3_returnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> result = controller.hello3();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Another dummy text for hello3", result.get("message"));
    }

    @Test
    void testHello_returnsUnmodifiableMap() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> result = controller.hello();

        assertThrows(UnsupportedOperationException.class, () -> result.put("newKey", "value"),
                "Map.of should return an unmodifiable map and throw on put");
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"),
                "Map.of should return an unmodifiable map and throw on remove");
    }

    @Test
    void testMultipleCalls_returnConsistentValues() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertNotNull(first);
        assertNotNull(second);
        assertEquals(first, second, "Multiple calls should return equal maps with same content");
        // Ensure both are unmodifiable independently
        assertAll(
                () -> assertThrows(UnsupportedOperationException.class, () -> first.put("x", "y")),
                () -> assertThrows(UnsupportedOperationException.class, () -> second.put("x", "y"))
        );
    }
}