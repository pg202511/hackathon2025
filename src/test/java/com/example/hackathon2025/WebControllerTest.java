package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.ConcurrentModel;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class WebControllerTest {

    private WebController controller;

    @BeforeEach
    public void setUp() {
        controller = new WebController();
    }

    @Mock
    private Model mockModel;

    @Test
    public void testIndexReturnsViewNameAndAddsTitle_withMockModel() {
        // Act
        String view = controller.index(mockModel);

        // Assert view name
        assertEquals("index", view, "index(...) should return the view name 'index'");

        // Verify addAttribute called with expected key and value
        verify(mockModel, times(1)).addAttribute("title", "Hackathon 2025 Demo");

        // Ensure no other interactions occurred
        verifyNoMoreInteractions(mockModel);
    }

    @Test
    public void testIndexAddsTitleToRealModel() {
        // Use a real Model implementation to verify attribute stored
        Model realModel = new ConcurrentModel();

        String view = controller.index(realModel);

        assertEquals("index", view);
        Object title = realModel.asMap().get("title");
        assertNotNull(title, "Model should contain a 'title' attribute after index(...)");
        assertEquals("Hackathon 2025 Demo", title);
    }

    @Test
    public void testIndexWithNullModel_throwsNullPointerException() {
        // Passing null should produce a NullPointerException because addAttribute is invoked on the model
        assertThrows(NullPointerException.class, () -> controller.index(null));
    }

    @Test
    public void testIndex_addAttributeCalledWithExactArguments_usingArgumentCaptor() {
        // Use ArgumentCaptor to assert exact types/values passed to addAttribute
        ArgumentCaptor<String> keyCaptor = ArgumentCaptor.forClass(String.class);
        ArgumentCaptor<Object> valueCaptor = ArgumentCaptor.forClass(Object.class);

        controller.index(mockModel);

        verify(mockModel).addAttribute(keyCaptor.capture(), valueCaptor.capture());
        assertEquals("title", keyCaptor.getValue());
        assertEquals("Hackathon 2025 Demo", valueCaptor.getValue());
    }
}