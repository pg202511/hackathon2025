package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class Hello2RestController {
    @GetMapping("/api/hello2alt")
    public Map<String,String> hello2alt() {
        return Map.of("message","Hello2 vom neuen REST-Controller!!");
    }
}

