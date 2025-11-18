package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class WebControllerTest {

    @Test
    @DisplayName("index should return view name 'index' and add title attribute to model")
    void indexReturnsViewAndAddsTitle() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();

        String view = controller.index(model);

        assertEquals("index", view, "Expected view name to be 'index'");
        assertTrue(model.containsKey("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Title attribute should be set to the demo text");
    }

    @Test
    @DisplayName("index should overwrite existing title attribute in the model")
    void indexOverwritesExistingTitle() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "Old Title");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Existing title should be overwritten with new value");
    }

    @Test
    @DisplayName("index should call addAttribute on the provided Model")
    void indexUsesModelAddAttributeWhenModelIsMocked() {
        WebController controller = new WebController();
        Model mockModel = mock(Model.class);

        String view = controller.index(mockModel);

        assertEquals("index", view);
        verify(mockModel).addAttribute("title", "Hackathon 2025 Demo");
    }

    @Test
    @DisplayName("index should throw NullPointerException when model is null")
    void indexThrowsOnNullModel() {
        WebController controller = new WebController();

        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with null Model should throw NullPointerException");
    }
}