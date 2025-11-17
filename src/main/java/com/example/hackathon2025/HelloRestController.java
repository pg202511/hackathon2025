package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class HelloRestController {
    @GetMapping("/api/hello")
    public Map<String,String> hello() {
        return Map.of("message","Hello from REST API for Hackathon 2025!");
    }
}
