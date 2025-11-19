package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class FibonacciRestController {

    @GetMapping("/api/fibonacci")
    public Map<String, Object> fibonacci(@RequestParam(value = "number", defaultValue = "0") int number) {
        if (number < 0) {
            return Map.of("error", "Die Zahl muss >= 0 sein.");
        }
        return Map.of(
            "number", number,
            "fibonacci", calculateFibonacci(number)
        );
    }

    private long calculateFibonacci(int n) {
        if (n <= 1) return n;
        long a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            long temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }
}

