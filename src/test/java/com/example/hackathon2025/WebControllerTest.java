package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    private WebController controller;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void indexReturnsIndexViewAndAddsTitleToModel() {
        Model model = new ExtendedModelMap();

        String viewName = controller.index(model);

        assertEquals("index", viewName, "Expected view name to be 'index'");
        assertTrue(model.asMap().containsKey("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"),
                "Model 'title' attribute should have the expected value");
    }

    @Test
    void indexUsesModelAddAttribute_whenModelIsMocked() {
        Model mockModel = Mockito.mock(Model.class);
        // ensure fluent API doesn't break if controller relies on return value (it doesn't, but safe)
        Mockito.when(mockModel.addAttribute(Mockito.anyString(), Mockito.any())).thenReturn(mockModel);

        String viewName = controller.index(mockModel);

        assertEquals("index", viewName);
        Mockito.verify(mockModel).addAttribute("title", "Hackathon 2025 Demo");
        Mockito.verifyNoMoreInteractions(mockModel);
    }

    @Test
    void indexThrowsNullPointerException_whenModelIsNull() {
        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with null Model should throw NullPointerException");
    }

    @Test
    void indexIsIdempotent_whenCalledMultipleTimesOnSameModel() {
        Model model = new ExtendedModelMap();

        String first = controller.index(model);
        String second = controller.index(model);

        assertEquals("index", first);
        assertEquals("index", second);
        // The attribute should still be present and have the expected value
        assertEquals("Hackathon 2025 Demo", model.asMap().get("title"));
    }
}