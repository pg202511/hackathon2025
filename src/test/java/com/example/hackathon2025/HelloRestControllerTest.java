package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    @Test
    void testHelloReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Resulting map should not be null");
        assertEquals(1, result.size(), "Resulting map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Map should contain 'message' key");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", result.get("message"),
                "Message should match expected text for hello()");
    }

    @Test
    void testHello2ReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello2();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Dummy text for hello2", result.get("message"));
    }

    @Test
    void testHello3ReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello3();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Another dummy text for hello3", result.get("message"));
    }

    @Test
    void testDifferentEndpointsReturnDifferentMessages() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> r1 = controller.hello();
        Map<String, String> r2 = controller.hello2();
        Map<String, String> r3 = controller.hello3();

        assertEquals("Hello again and again from REST API for Hackathon 2025!", r1.get("message"));
        assertEquals("Dummy text for hello2", r2.get("message"));
        assertEquals("Another dummy text for hello3", r3.get("message"));

        // Ensure the messages differ where expected
        assertNotEquals(r1.get("message"), r2.get("message"));
        assertNotEquals(r1.get("message"), r3.get("message"));
        assertNotEquals(r2.get("message"), r3.get("message"));
    }

    @Test
    void testReturnedMapsAreUnmodifiable() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> m1 = controller.hello();
        Map<String, String> m2 = controller.hello2();
        Map<String, String> m3 = controller.hello3();

        // Attempting modification should throw UnsupportedOperationException
        assertThrows(UnsupportedOperationException.class, () -> m1.put("newKey", "newValue"));
        assertThrows(UnsupportedOperationException.class, () -> m2.put("newKey", "newValue"));
        assertThrows(UnsupportedOperationException.class, () -> m3.put("newKey", "newValue"));

        assertThrows(UnsupportedOperationException.class, () -> m1.remove("message"));
        assertThrows(UnsupportedOperationException.class, () -> m2.clear());
        assertThrows(UnsupportedOperationException.class, () -> m3.putAll(Map.of("a", "b")));
    }

    @Test
    void testRepeatedCallsReturnConsistentContent() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        // content equality should hold across calls
        assertEquals(first, second);
        assertEquals(first.size(), 1);
        assertEquals("Hello again and again from REST API for Hackathon 2025!", second.get("message"));
    }
}