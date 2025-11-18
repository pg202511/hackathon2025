package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class GoodbyRestController {

    @GetMapping("/api/goodby")
    public Map<String, String> goodby(@RequestParam(value = "name", defaultValue = "Gast") String name) {
        return Map.of("message", "Goodbye, " + name + ", from REST API for Hackathon 2025!!!");
    }

    @GetMapping("/api/goodnight")
    public Map<String, String> goodnight() {
        return Map.of("message", "Good night from REST API for Hackathon 2025!!!");
    }
}
