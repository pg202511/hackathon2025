package com.example.hackathon2025;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;

import java.lang.annotation.Annotation;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WebControllerTest {

    private WebController controller;

    @Mock
    private Model model;

    @BeforeEach
    void setUp() {
        controller = new WebController();
    }

    @Test
    void index_shouldReturnIndexViewAndSetTitleAttribute() {
        // Act
        String viewName = controller.index(model);

        // Assert
        assertEquals("index", viewName, "Expected view name to be 'index'");

        // Verify model interaction
        verify(model, times(1)).addAttribute("title", "Hackathon 2025 Demo");
        verifyNoMoreInteractions(model);
    }

    @Test
    void index_withNullModel_shouldThrowNullPointerException() {
        // Act & Assert
        assertThrows(NullPointerException.class, () -> controller.index(null),
                "Calling index with a null Model should throw NullPointerException because addAttribute is invoked");
    }

    @Test
    void classAndMethod_shouldHaveSpringAnnotations() throws Exception {
        Class<?> clazz = WebController.class;

        // Verify class has an annotation named "Controller" (to avoid hard dependency on the annotation type)
        boolean hasControllerAnnotation = Arrays.stream(clazz.getAnnotations())
                .map(Annotation::annotationType)
                .map(Class::getSimpleName)
                .anyMatch(name -> "Controller".equals(name));
        assertTrue(hasControllerAnnotation, "WebController should be annotated with @Controller");

        // Find the "index" method
        Optional<Method> indexMethodOpt = Arrays.stream(clazz.getDeclaredMethods())
                .filter(m -> "index".equals(m.getName()))
                .findFirst();
        assertTrue(indexMethodOpt.isPresent(), "Expected an 'index' method to be present");
        Method indexMethod = indexMethodOpt.get();

        // Verify method has an annotation named "GetMapping"
        Optional<Annotation> getMappingAnnOpt = Arrays.stream(indexMethod.getAnnotations())
                .filter(a -> "GetMapping".equals(a.annotationType().getSimpleName()))
                .findFirst();
        assertTrue(getMappingAnnOpt.isPresent(), "index method should be annotated with @GetMapping");

        // Inspect the annotation to ensure it maps to "/"
        Annotation getMappingAnn = getMappingAnnOpt.get();

        // Try to read "value" or "path" element of the annotation reflectively
        String[] paths = null;
        try {
            Method valueMethod = getMappingAnn.annotationType().getMethod("value");
            Object val = valueMethod.invoke(getMappingAnn);
            if (val instanceof String[]) {
                paths = (String[]) val;
            }
        } catch (NoSuchMethodException ignored) {
            // ignore and try "path"
        }

        if (paths == null) {
            try {
                Method pathMethod = getMappingAnn.annotationType().getMethod("path");
                Object val = pathMethod.invoke(getMappingAnn);
                if (val instanceof String[]) {
                    paths = (String[]) val;
                }
            } catch (NoSuchMethodException ignored) {
                // no path either
            }
        }

        assertNotNull(paths, "Could not read paths from @GetMapping annotation (no 'value' or 'path' attribute found)");
        // Expect at least one mapping and that one of them equals "/"
        assertTrue(paths.length > 0, "Expected at least one mapping path in @GetMapping");
        boolean containsRoot = Arrays.stream(paths).anyMatch(s -> "/".equals(s));
        assertTrue(containsRoot, "Expected @GetMapping to contain mapping for '/'");
    }
}