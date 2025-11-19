package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.Model;
import org.springframework.ui.ExtendedModelMap;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    @Test
    void indexReturnsIndexViewAndAddsTitle() {
        WebController controller = new WebController();
        Model model = new ExtendedModelMap();

        String view = controller.index(model);

        assertEquals("index", view, "Expected view name to be 'index'");
        Object title = ((ExtendedModelMap) model).get("title");
        assertNotNull(title, "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", title);
    }

    @Test
    void indexOverwritesExistingTitleAttribute() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Controller should overwrite existing 'title' attribute");
    }

    @Test
    void indexMultipleInvocationsKeepsTitleConsistent() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();

        String first = controller.index(model);
        String second = controller.index(model);

        assertEquals("index", first);
        assertEquals("index", second);
        assertEquals("Hackathon 2025 Demo", model.get("title"));
    }

    @Test
    void indexWithNullModelThrowsNullPointerException() {
        WebController controller = new WebController();
        assertThrows(NullPointerException.class, () -> controller.index(null), "Calling index with null model should throw NPE");
    }
}