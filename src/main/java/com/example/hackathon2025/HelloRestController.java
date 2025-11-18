package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class HelloRestController {
    @GetMapping("/api/hello")
    public Map<String,String> hello() {
        return Map.of("message","Hello again and again from REST API for Hackathon 2025!");
    }

    @GetMapping("/api/hello2")
    public Map<String,String> hello2() {
        return Map.of("message","Dummy text for hello2");
    }

    @GetMapping("/api/hello3")
    public Map<String,String> hello3() {
        return Map.of("message","Another dummy text for hello3");
    }
}
