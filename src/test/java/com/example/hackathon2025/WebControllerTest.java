package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class WebControllerTest {

    private WebController controller;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void index_shouldReturnIndexView_andAddTitleAttribute() {
        // Arrange
        Model model = mock(Model.class);

        // Act
        String view = controller.index(model);

        // Assert
        assertEquals("index", view, "Controller should return view name 'index'");
        verify(model, times(1)).addAttribute("title", "Hackathon 2025 Demo");
        verifyNoMoreInteractions(model);
    }

    @Test
    void index_withNullModel_shouldThrowNullPointerException() {
        // If a null Model is passed, addAttribute will cause a NPE — ensure this behavior is visible.
        assertThrows(NullPointerException.class, () -> controller.index(null));
    }

    @Test
    void index_whenModelThrowsException_shouldPropagateException() {
        // Arrange
        Model model = mock(Model.class);
        doThrow(new IllegalStateException("model failure")).when(model).addAttribute(anyString(), any());

        // Act & Assert
        IllegalStateException ex = assertThrows(IllegalStateException.class, () -> controller.index(model));
        assertEquals("model failure", ex.getMessage());
        verify(model, times(1)).addAttribute("title", "Hackathon 2025 Demo");
    }
}