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

        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should contain exactly one entry");
        assertEquals(Set.of("message"), result.keySet(), "Map should only contain the 'message' key");
        assertEquals("Hello again and again from REST API for Hackathon 2025!", result.get("message"));
    }

    @Test
    void testHello2_returnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello2();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.containsKey("message"));
        assertEquals("Dummy text for hello2", result.get("message"));
    }

    @Test
    void testHello3_returnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello3();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertTrue(result.containsKey("message"));
        assertEquals("Another dummy text for hello3", result.get("message"));
    }

    @Test
    void testReturnedMapsAreImmutable() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> m1 = controller.hello();
        Map<String, String> m2 = controller.hello2();
        Map<String, String> m3 = controller.hello3();

        assertThrows(UnsupportedOperationException.class, () -> m1.put("newKey", "value"));
        assertThrows(UnsupportedOperationException.class, () -> m2.remove("message"));
        assertThrows(UnsupportedOperationException.class, () -> m3.clear());
    }

    @Test
    void testMultipleInvocationsProduceEqualContent() {
        HelloRestController controller = new HelloRestController();

        Map<String, String> firstCall = controller.hello();
        Map<String, String> secondCall = controller.hello();

        assertEquals(firstCall, secondCall, "Multiple invocations should produce equal maps (same content)");
    }

    @Test
    void testDifferentEndpointsReturnDifferentMessages() {
        HelloRestController controller = new HelloRestController();

        String v1 = controller.hello().get("message");
        String v2 = controller.hello2().get("message");
        String v3 = controller.hello3().get("message");

        // ensure they are not all equal; specifically check pairwise differences where expected
        assertNotEquals(v1, v2, "hello and hello2 should return different messages");
        assertNotEquals(v1, v3, "hello and hello3 should return different messages");
        // hello2 and hello3 are different as well
        assertNotEquals(v2, v3, "hello2 and hello3 should return different messages");
    }
}