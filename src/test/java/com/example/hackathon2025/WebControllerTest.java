package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import java.util.Collections;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class WebControllerTest {

    @Test
    public void testIndexAddsTitleAndReturnsView() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();

        String viewName = controller.index(model);

        assertEquals("index", viewName, "Expected view name to be 'index'");
        assertTrue(((ExtendedModelMap) model).containsAttribute("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", ((ExtendedModelMap) model).get("title"));
    }

    @Test
    public void testIndexOverridesExistingTitleValue() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertEquals("Hackathon 2025 Demo", model.get("title"), "The controller should replace an existing 'title' attribute");
        // Ensure no unexpected additional attributes were added
        Map<String, Object> asMap = model.asMap();
        assertEquals(Collections.singleton("title"), asMap.keySet(), "Only 'title' key should be present in the model");
    }

    @Test
    public void testIndexWithNullModelThrowsNullPointerException() {
        WebController controller = new WebController();
        assertThrows(NullPointerException.class, () -> controller.index(null), "Passing a null Model should result in NPE");
    }
}