package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    @Test
    void index_whenCalled_returnsIndexViewAndSetsTitle() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();

        String viewName = controller.index(model);

        assertEquals("index", viewName, "Expected view name to be 'index'");
        assertTrue(model.asMap().containsKey("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"), "Title attribute should match expected value");
    }

    @Test
    void index_overwritesExistingTitleAttribute() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"), "Existing title should be overwritten with demo title");
    }

    @Test
    void index_preservesOtherAttributes() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();
        model.addAttribute("otherKey", 123);

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertEquals(123, model.asMap().get("otherKey"), "Other attributes should be preserved");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"));
    }

    @Test
    void index_withNullModel_throwsNullPointerException() {
        WebController controller = new WebController();

        assertThrows(NullPointerException.class, () -> controller.index(null), "Passing null model should throw NullPointerException");
    }
}