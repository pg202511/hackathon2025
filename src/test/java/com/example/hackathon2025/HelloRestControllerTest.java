package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.bind.annotation.GetMapping;

import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private HelloRestController controller;

    private static final String EXPECTED_MESSAGE = "Hello again and again from REST API for Hackathon 2025!";

    @BeforeEach
    void setUp() {
        controller = new HelloRestController();
    }

    @Test
    void hello_shouldReturnNonNullMapContainingMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Returned map must contain the key 'message'");

        String message = result.get("message");
        assertNotNull(message, "Message value should not be null");
        assertFalse(message.isEmpty(), "Message value should not be empty");

        // Exact content verification (detects regressions)
        assertEquals(EXPECTED_MESSAGE, message, "Message content should match expected text");
    }

    @Test
    void hello_shouldReturnImmutableMap() {
        Map<String, String> result = controller.hello();

        assertNotNull(result);

        // Attempting to modify the Map should throw UnsupportedOperationException for Map.of result
        assertThrows(UnsupportedOperationException.class, () -> result.put("newKey", "newValue"),
                "Returned map should be immutable and reject put operations");
    }

    @Test
    void hello_multipleInvocationsShouldReturnSameContent() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertNotNull(first);
        assertNotNull(second);

        // Content equality is important; instance equality is not required
        assertEquals(first, second, "Multiple invocations should return equal maps (same content)");
    }

    @Test
    void hello_methodShouldBeAnnotatedWithGetMappingForApiHello() throws NoSuchMethodException {
        Method method = HelloRestController.class.getMethod("hello");
        GetMapping mapping = method.getAnnotation(GetMapping.class);

        assertNotNull(mapping, "hello() should be annotated with @GetMapping");

        // Check both 'value' and 'path' aliases for the expected endpoint
        String[] values = mapping.value();
        String[] paths = mapping.path();

        boolean containsExpected = Arrays.asList(values).contains("/api/hello") || Arrays.asList(paths).contains("/api/hello");
        assertTrue(containsExpected, "@GetMapping must map to '/api/hello'");
    }

    @Test
    void hello_messageShouldMentionHackathon2025() {
        Map<String, String> result = controller.hello();
        String message = result.get("message");

        assertNotNull(message);
        // Less brittle check to ensure purpose of message remains intact
        assertTrue(message.contains("Hackathon 2025"), "Message should reference 'Hackathon 2025'");
    }
}