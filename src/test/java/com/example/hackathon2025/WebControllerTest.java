package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    @Test
    void index_shouldReturnIndexViewAndSetTitleAttribute() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();

        String viewName = controller.index(model);

        assertEquals("index", viewName, "Expected view name to be 'index'");
        assertTrue(model.containsAttribute("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.get("title"));
    }

    @Test
    void index_shouldOverwriteExistingTitleAttribute() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        // pre-populate with a different title
        model.addAttribute("title", "Old Title");
        model.addAttribute("other", 123);

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        // title should be overwritten by controller
        assertEquals("Hackathon 2025 Demo", model.get("title"));
        // other attributes should remain untouched
        assertEquals(123, model.get("other"));
    }

    @Test
    void index_shouldThrowWhenModelIsNull() {
        WebController controller = new WebController();
        Model nullModel = null;

        assertThrows(NullPointerException.class, () -> controller.index(nullModel),
                "Calling index with null Model should throw NullPointerException");
    }
}