package com.example.hackathon2025;

import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

public class WebControllerTest {

    @Test
    void indexReturnsViewNameAndSetsTitleInModel_usingConcreteModel() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();

        String view = controller.index(model);

        assertEquals("index", view, "Expected view name to be 'index'");
        assertTrue(model.containsAttribute("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Title attribute should be set to demo text");
    }

    @Test
    void indexOverwritesExistingTitleInModel() {
        WebController controller = new WebController();
        ExtendedModelMap model = new ExtendedModelMap();
        model.addAttribute("title", "old value");

        String view = controller.index(model);

        assertEquals("index", view);
        assertEquals("Hackathon 2025 Demo", model.get("title"), "Existing title should be overwritten");
    }

    @Test
    void indexInvokesAddAttributeOnProvidedModel_mockedModel() {
        WebController controller = new WebController();
        Model mockModel = mock(Model.class);

        // call method under test
        String view = controller.index(mockModel);

        // verify behavior on mock and return value
        assertEquals("index", view);
        verify(mockModel).addAttribute("title", "Hackathon 2025 Demo");
    }

    @Test
    void indexWithNullModelThrowsNullPointerException() {
        WebController controller = new WebController();

        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Passing null model should result in a NullPointerException");
    }
}