package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.ConcurrentModel;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WebControllerTest {

    private WebController controller;

    @Mock
    private Model mockModel;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void index_shouldReturnViewNameAndAddTitleAttribute_whenModelIsMock() {
        // Act
        String view = controller.index(mockModel);

        // Assert return value
        assertEquals("index", view, "Controller should return the 'index' view name");

        // Verify interaction with model
        verify(mockModel, times(1)).addAttribute("title", "Hackathon 2025 Demo");
        verifyNoMoreInteractions(mockModel);
    }

    @Test
    void index_shouldAddTitleAttributeToRealModelImplementation() {
        // Use a real Model implementation to ensure attribute is actually stored
        Model realModel = new ConcurrentModel();

        String view = controller.index(realModel);

        assertEquals("index", view, "Controller should return the 'index' view name");
        Object title = realModel.getAttribute("title");
        assertNotNull(title, "Title attribute should be set on the model");
        assertEquals("Hackathon 2025 Demo", title, "Title attribute should match the expected text");
    }

    @Test
    void index_shouldThrowNullPointerException_whenModelIsNull() {
        // Explicitly verify null handling - production method expects a non-null Model
        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with null model is expected to throw NullPointerException");
    }
}