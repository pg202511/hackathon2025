package com.example.hackathon2025;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {
    @GetMapping("/")
    public String index(Model m){
        m.addAttribute("title","Hackathon 2025 Demo");
        return "index";
    }
}
// trigger test
