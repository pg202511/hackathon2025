package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.ui.ConcurrentModel;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;

class WebControllerTest {

    private WebController controller;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void indexReturnsViewAndAddsTitle_usingConcurrentModel() {
        ConcurrentModel model = new ConcurrentModel();

        String view = controller.index(model);

        assertEquals("index", view, "Controller should return the 'index' view name");
        assertTrue(model.containsAttribute("title"), "Model should contain 'title' attribute");
        assertEquals("Hackathon 2025 Demo", model.getAttribute("title"), "Title attribute should match expected value");
    }

    @Test
    void indexAddsTitleToMockModelAndReturnsIndex() {
        Model mockModel = Mockito.mock(Model.class);

        String view = controller.index(mockModel);

        assertEquals("index", view, "Controller should return the 'index' view name");
        Mockito.verify(mockModel).addAttribute("title", "Hackathon 2025 Demo");
        Mockito.verifyNoMoreInteractions(mockModel);
    }

    @Test
    void indexWithNullModelThrowsNullPointerException() {
        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with null Model should result in NullPointerException");
    }
}