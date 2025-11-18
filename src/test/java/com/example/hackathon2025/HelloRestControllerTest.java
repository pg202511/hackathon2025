package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class HelloRestControllerTest {

    private HelloRestController controller;
    private static final String EXPECTED_KEY = "message";
    private static final String EXPECTED_VALUE = "Hello again and again from REST API for Hackathon 2025!";

    @BeforeEach
    void setUp() {
        controller = new HelloRestController();
    }

    @Test
    @DisplayName("Normalfall: hello() liefert nicht-null Map mit erwarteter Nachricht")
    void testHelloReturnsExpectedMessage() {
        Map<String, String> result = controller.hello();

        assertNotNull(result, "Die zurückgegebene Map darf nicht null sein");
        assertEquals(1, result.size(), "Die Map sollte genau ein Entry enthalten");
        assertTrue(result.containsKey(EXPECTED_KEY), "Die Map sollte den Key 'message' enthalten");
        assertEquals(EXPECTED_VALUE, result.get(EXPECTED_KEY), "Der Wert für 'message' stimmt nicht überein");
    }

    @Test
    @DisplayName("Edge Case: mehrfacher Aufruf liefert konsistente Inhalte")
    void testMultipleInvocationsReturnConsistentContent() {
        Map<String, String> first = controller.hello();
        Map<String, String> second = controller.hello();

        assertNotNull(first);
        assertNotNull(second);

        // Inhalt sollte gleich sein
        assertEquals(first, second, "Die Inhalte mehrerer Aufrufe sollten gleich sein");
        // explizit prüfen, dass erwarteter Key und Wert vorhanden sind
        assertEquals(EXPECTED_VALUE, second.get(EXPECTED_KEY));
    }

    @Test
    @DisplayName("Fehlerfall / Edge: zurückgegebene Map ist unveränderlich")
    void testReturnedMapIsImmutable() {
        Map<String, String> result = controller.hello();

        assertThrows(UnsupportedOperationException.class, () -> result.put("newKey", "value"),
                "Die zurückgegebene Map sollte unveränderlich sein und put sollte UnsupportedOperationException werfen");

        assertThrows(UnsupportedOperationException.class, () -> result.remove(EXPECTED_KEY),
                "remove sollte UnsupportedOperationException werfen");

        assertThrows(UnsupportedOperationException.class, result::clear,
                "clear sollte UnsupportedOperationException werfen");
    }

    @Test
    @DisplayName("Inhaltliche Prüfung: Nachricht enthält erwartete Stichworte")
    void testMessageContainsKeywords() {
        String value = controller.hello().get(EXPECTED_KEY);
        assertNotNull(value, "Nachricht darf nicht null sein");
        assertFalse(value.isBlank(), "Nachricht darf nicht leer oder nur Whitespaces sein");
        assertTrue(value.startsWith("Hello"), "Nachricht sollte mit 'Hello' beginnen");
        assertTrue(value.contains("Hackathon 2025"), "Nachricht sollte 'Hackathon 2025' enthalten");
    }
}