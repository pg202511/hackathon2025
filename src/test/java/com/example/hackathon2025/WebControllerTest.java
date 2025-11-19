package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    @Test
    void index_ShouldReturnIndexViewAndAddTitleAttribute() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();

        String viewName = controller.index(model);

        assertEquals("index", viewName, "Expected view name to be 'index'");
        assertTrue(model.containsAttribute("title"), "Model should contain 'title' attribute");
        Object titleValue = ((ExtendedModelMap) model).get("title");
        assertEquals("Hackathon 2025 Demo", titleValue, "Title attribute should be set to demo text");
    }

    @Test
    void index_ShouldOverwriteExistingTitleAttribute() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertTrue(model.containsAttribute("title"));
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Existing title should be overwritten");
    }

    @Test
    void index_WithAdditionalAttributes_ShouldPreserveOtherAttributes() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("other", 42);

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertTrue(model.containsAttribute("other"), "Other attributes should be preserved");
        assertEquals(42, model.get("other"));
        assertEquals("Hackathon 2025 Demo", model.get("title"));
    }

    @Test
    void index_NullModel_ShouldThrowNullPointerException() {
        WebController controller = new WebController();

        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with null model should throw NullPointerException");
    }

    @Test
    void index_MultipleInvocations_ShouldBeIdempotentForTitle() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();

        String first = controller.index(model);
        String second = controller.index(model);

        assertEquals("index", first);
        assertEquals("index", second);
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Title should remain the same after multiple calls");
    }
}