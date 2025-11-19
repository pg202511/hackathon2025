package com.example.hackathon2025;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.Random;

@RestController
public class NatureImageRestController {

    private final Map<String, List<String>> imageUrls = Map.of(
        "tree", List.of(
            "https://picsum.photos/id/1011/600/400",
            "https://picsum.photos/id/102/600/400",
            "https://picsum.photos/id/104/600/400"
        ),
        "river", List.of(
            "https://picsum.photos/id/1056/600/400",
            "https://picsum.photos/id/106/600/400",
            "https://picsum.photos/id/1074/600/400"
        ),
        "mountain", List.of(
            "https://picsum.photos/id/1003/600/400",
            "https://picsum.photos/id/1016/600/400",
            "https://picsum.photos/id/1025/600/400"
        )
        // Weitere Begriffe und URLs nach Bedarf ergänzen
    );

    @GetMapping("/api/nature-image")
    public Map<String, String> getRandomNatureImage(@RequestParam String keyword) {
        List<String> urls = imageUrls.getOrDefault(keyword.toLowerCase(), List.of(
            "https://picsum.photos/seed/" + keyword + "/600/400"
        ));
        String url = urls.get(new Random().nextInt(urls.size()));
        return Map.of("keyword", keyword, "imageUrl", url);
    }
}

