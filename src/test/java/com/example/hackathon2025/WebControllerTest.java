package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    private WebController controller;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void index_shouldReturnIndexViewAndSetTitleAttribute() {
        Model model = new ExtendedModelMap();

        String view = controller.index(model);

        assertEquals("index", view, "The controller should return the 'index' view name.");
        assertTrue(((ExtendedModelMap) model).asMap().containsKey("title"), "Model should contain a 'title' attribute.");
        assertEquals("Hackathon 2025 Demo",
                ((ExtendedModelMap) model).asMap().get("title"),
                "The 'title' attribute should be set to the expected demo text.");
    }

    @Test
    void index_shouldOverwriteExistingTitleAttribute() {
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"),
                "The controller should overwrite any existing 'title' attribute with the demo text.");
    }

    @Test
    void index_shouldPreserveOtherAttributes() {
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("foo", 42);

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals(42, model.asMap().get("foo"), "Attributes other than 'title' should be preserved.");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"));
    }

    @Test
    void index_whenModelIsNull_shouldThrowNullPointerException() {
        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with a null Model should throw a NullPointerException.");
    }

    @Test
    void multipleInvocations_withDifferentModels_areIndependent() {
        ExtendedModelMap model1 = new ExtendedModelMap();
        ExtendedModelMap model2 = new ExtendedModelMap();
        model2.addAttribute("title", "previous");

        String view1 = controller.index(model1);
        String view2 = controller.index(model2);

        assertEquals("index", view1);
        assertEquals("index", view2);
        assertEquals("Hackathon 2025 Demo", model1.asMap().get("title"));
        assertEquals("Hackathon 2025 Demo", model2.asMap().get("title"),
                "Each invocation should set the title on the provided Model independently.");
    }
}