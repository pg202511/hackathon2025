package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.web.bind.annotation.RequestParam;

import java.lang.reflect.Method;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class GoodbyRestControllerTest {

    @Test
    void testGoodby_withName_returnsExpectedMessage() {
        GoodbyRestController controller = new GoodbyRestController();
        Map<String, String> result = controller.goodby("Alice");

        assertNotNull(result, "Result map should not be null");
        assertEquals(1, result.size(), "Result map should contain exactly one entry");
        assertTrue(result.containsKey("message"), "Result map should contain 'message' key");
        assertEquals("Goodbye, Alice, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withEmptyString_returnsMessageWithEmptyName() {
        GoodbyRestController controller = new GoodbyRestController();
        Map<String, String> result = controller.goodby("");

        assertNotNull(result);
        assertEquals("Goodbye, , from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withNull_returnsMessageContainingNullLiteral() {
        GoodbyRestController controller = new GoodbyRestController();
        // Calling directly with null (framework default not applied when calling method directly)
        Map<String, String> result = controller.goodby(null);

        assertNotNull(result);
        assertEquals("Goodbye, null, from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_withSpecialCharacters() {
        GoodbyRestController controller = new GoodbyRestController();
        String name = "ÄÖÜ-测试-!@#";
        Map<String, String> result = controller.goodby(name);

        assertNotNull(result);
        assertEquals("Goodbye, " + name + ", from REST API for Hackathon 2025!!!!", result.get("message"));
    }

    @Test
    void testGoodby_requestParamAnnotationHasDefaultValueGast() throws NoSuchMethodException {
        Method method = GoodbyRestController.class.getMethod("goodby", String.class);
        RequestParam rp = method.getParameters()[0].getAnnotation(RequestParam.class);
        assertNotNull(rp, "Parameter should be annotated with @RequestParam");
        assertEquals("Gast", rp.defaultValue(), "The defaultValue on @RequestParam should be 'Gast'");
    }

    @Test
    void testGoodnight_returnsExpectedMessage() {
        GoodbyRestController controller = new GoodbyRestController();
        Map<String, String> result = controller.goodnight();

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Good night from REST API for Hackathon 2025!!!", result.get("message"));
    }

    @Test
    void testReturnedMapsAreUnmodifiable() {
        GoodbyRestController controller = new GoodbyRestController();
        Map<String, String> r1 = controller.goodby("Bob");
        Map<String, String> r2 = controller.goodnight();

        assertThrows(UnsupportedOperationException.class, () -> r1.put("newKey", "newValue"));
        assertThrows(UnsupportedOperationException.class, () -> r2.put("another", "value"));
    }
}