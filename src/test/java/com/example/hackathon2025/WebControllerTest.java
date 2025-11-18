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

        String viewName = controller.index(model);

        assertEquals("index", viewName, "The view name should be 'index'");
        assertTrue(model.asMap().containsKey("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"),
                "The 'title' attribute should be 'Hackathon 2025 Demo'");
        // Ensure no unexpected attributes were added
        assertEquals(1, model.asMap().size(), "Model should contain exactly one attribute after invocation");
    }

    @Test
    void index_shouldOverrideExistingTitleAttributeIfPresent() {
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");
        model.addAttribute("other", "keepMe");

        String viewName = controller.index(model);

        assertEquals("index", viewName);
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"),
                "Existing 'title' attribute should be overwritten by controller");
        // Ensure other attributes are preserved
        assertEquals("keepMe", model.asMap().get("other"), "Other attributes should remain untouched");
        assertTrue(model.asMap().containsKey("other"));
    }

    @Test
    void index_withNullModel_shouldThrowNullPointerException() {
        // The controller expects a non-null Model. Passing null should result in a NullPointerException
        assertThrows(NullPointerException.class, () -> controller.index(null));
    }

    @Test
    void index_multipleInvocations_shouldBeIdempotentRegardingTitleValue() {
        ExtendedModelMap model = new ExtendedModelMap();

        String first = controller.index(model);
        String second = controller.index(model);

        assertEquals("index", first);
        assertEquals("index", second);
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"),
                "Repeated invocations should keep the same title value");
        // Still only one title entry
        assertEquals(1, model.asMap().size());
    }
}