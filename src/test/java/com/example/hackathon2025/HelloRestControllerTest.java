package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.web.bind.annotation.GetMapping;

import java.lang.reflect.Method;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class HelloRestControllerTest {

    private static final String EXPECTED_KEY = "message";
    private static final String EXPECTED_VALUE = "Hello again and again from REST API for Hackathon 2025!";

    @Test
    void testHelloReturnsExpectedMessage() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Returned map should not be null");
        assertEquals(1, result.size(), "Returned map should contain exactly one entry");
        assertTrue(result.containsKey(EXPECTED_KEY), "Returned map should contain the key 'message'");
        assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY), "Returned message must match expected text");

        // Ensure no extra keys
        assertEquals(Set.of(EXPECTED_KEY), result.keySet(), "Map should only contain the 'message' key");
    }

    @Test
    void testHelloValueIsNonEmpty() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        String value = result.get(EXPECTED_KEY);
        assertNotNull(value, "Message value should not be null");
        assertFalse(value.isBlank(), "Message value should not be blank");
        assertTrue(value.length() > 10, "Message value should be reasonably long");
    }

    @Test
    void testHelloMapIsImmutable() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> result = controller.hello();

        // Attempting mutation should throw UnsupportedOperationException for Map.of immutable map
        assertThrows(UnsupportedOperationException.class, () -> result.put("another", "x"));
        assertThrows(UnsupportedOperationException.class, () -> result.remove(EXPECTED_KEY));
        assertThrows(UnsupportedOperationException.class, () -> result.clear());

        // Original content still intact
        assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY));
    }

    @Test
    void testMultipleCallsReturnEquivalentMaps() {
        HelloRestController controller = new HelloRestController();
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        // Should be value-equal across invocations
        assertEquals(first, second, "Consecutive calls should return maps with equal content");

        // Each entry should be non-null
        first.forEach((k, v) -> {
            assertNotNull(k, "Key must not be null");
            assertNotNull(v, "Value must not be null");
        });
    }

    @Test
    void testHelloMethodHasGetMappingWithExpectedPath() throws NoSuchMethodException {
        // Validate that the hello() method is annotated with @GetMapping and contains the expected path
        Method helloMethod = HelloRestController.class.getMethod("hello");
        GetMapping mapping = helloMethod.getAnnotation(GetMapping.class);
        assertNotNull(mapping, "hello() should be annotated with @GetMapping");

        // Check both value and path attributes (either may be used)
        String[] values = mapping.value();
        String[] paths = mapping.path();

        boolean containsExpected = contains("/api/hello", values) || contains("/api/hello", paths);
        assertTrue(containsExpected, "@GetMapping should map to '/api/hello'");
    }

    private static boolean contains(String expected, String[] arr) {
        if (arr == null) return false;
        for (String s : arr) {
            if (Objects.equals(expected, s)) return true;
        }
        return false;
    }
}