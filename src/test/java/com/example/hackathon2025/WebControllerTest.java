package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

public class WebControllerTest {

    private WebController controller;

    @BeforeEach
    public void setUp() {
        controller = new WebController();
    }

    @Test
    public void testIndexAddsTitleAndReturnsView() {
        Model model = new ExtendedModelMap();

        String view = controller.index(model);

        assertEquals("index", view, "Expected view name to be 'index'");
        assertTrue(model.containsAttribute("title"), "Model should contain attribute 'title'");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"));
        // ensure only the title attribute was added
        assertEquals(1, ((ExtendedModelMap) model).size());
    }

    @Test
    public void testIndexOverwritesExistingTitle() {
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Hackathon 2025 Demo", model.get("title"));
        // still only one entry for title
        assertEquals(1, model.size());
    }

    @Test
    public void testIndexPreservesOtherAttributes() {
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("user", "Alice");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Alice", model.get("user"), "Existing attributes should be preserved");
        assertEquals("Hackathon 2025 Demo", model.get("title"));
        // should have both attributes
        assertEquals(2, model.size());
    }

    @Test
    public void testIndexMultipleInvocationsIdempotentForTitle() {
        ExtendedModelMap model = new ExtendedModelMap();

        String firstView = controller.index(model);
        String secondView = controller.index(model);

        assertEquals("index", firstView);
        assertEquals("index", secondView);
        assertEquals("Hackathon 2025 Demo", model.get("title"));
        // repeated calls should not create multiple title entries
        assertEquals(1, model.size());
    }

    @Test
    public void testIndexWithNullModelThrowsNpe() {
        assertThrows(NullPointerException.class, () -> controller.index(null));
    }
}