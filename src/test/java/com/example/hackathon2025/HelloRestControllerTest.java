package com.example.hackathon2025;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private final HelloRestController controller = new HelloRestController();

    @Test
    void testHello_returnsExpectedMessage() {
        Map<String, String> result = controller.hello();
        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should contain exactly one entry");
        assertTrue(result.containsKey("message"),("Result map should contain key 'message'"));
        assertEquals("Hello again and again from REST API for Hackathon 2025!", result.get("message"));
    }

    @Test
    void testHello2_returnsExpectedMessage() {
        Map<String, String> result = controller.hello2();
        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Dummy text for hello2", result.get("message"));
    }

    @Test
    void testHello3_returnsExpectedMessage() {
        Map<String, String> result = controller.hello3();
        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Another dummy text for hello3", result.get("message"));
    }

    @Test
    void testMessagesAreDistinctBetweenEndpoints() {
        Map<String, String> r1 = controller.hello();
        Map<String, String> r2 = controller.hello2();
        Map<String, String> r3 = controller.hello3();

        assertNotEquals(r1.get("message"), r2.get("message"), "hello and hello2 messages should differ");
        assertNotEquals(r1.get("message"), r3.get("message"), "hello and hello3 messages should differ");
        assertNotEquals(r2.get("message"), r3.get("message"), "hello2 and hello3 messages should differ");
    }

    @Test
    void testReturnedMapsAreImmutable() {
        Map<String, String> result = controller.hello();
        assertThrows(UnsupportedOperationException.class, () -> result.put("newKey", "value"));
        assertThrows(UnsupportedOperationException.class, () -> result.remove("message"));
    }

    @Test
    void testReturnedMapHasNonEmptyMessage() {
        Map<String, String> result = controller.hello();
        String msg = result.get("message");
        assertNotNull(msg);
        assertFalse(msg.isBlank(), "message should not be blank");
        assertTrue(msg.length() > 5, "message should have a reasonable length");
    }
}