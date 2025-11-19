<!--
  This document was initially generated with the help of Azure OpenAI.
  Please review and adapt it as needed.
-->

# Architecture and Technical Overview — hackathon2025

This document describes the architecture, components, and operational practices of the hackathon2025 demo Spring Boot application. It is intended to help new developers understand how the project is structured, how requests flow through the system, what the UI does, how tests are organized, and what CI/CD/AI-assisted workflows exist. This document was produced by an AI-assisted workflow and should be reviewed and refined by humans (see CI/CD section).

## 1. Introduction

What the application does
- hackathon2025 is a small demo web application that exposes a few REST endpoints and a minimal web UI rendered with Thymeleaf.
- It demonstrates:
  - Serving an index page ("/") with a JavaScript button that calls a REST endpoint.
  - A followup UI page (templates/followup.html) that exercises multiple REST endpoints, including one that accepts a query parameter.
  - A set of simple REST endpoints that return JSON messages (used by the UI and tests).

Main technologies
- Java (Spring Boot)
- Spring MVC (REST controllers and Thymeleaf MVC controller)
- Thymeleaf templates for server-side HTML rendering
- REST APIs returning JSON (Map<String, String> serialized by Spring)
- Playwright for UI/API end-to-end tests (project contains Playwright test activities as part of CI)
- JUnit for unit tests
- Azure OpenAI is used in automated workflows to generate/update tests and documentation (see CI/CD section)

Assumption: CI workflows and AI-assisted test generation are referenced in the repository's automation; this document summarizes their intended behavior per the repository's conventions and the project description.

## 2. Architecture Overview

High-level architecture
- Single Spring Boot application that auto-detects components via @SpringBootApplication.
- Two layers are visible:
  - Web/UI layer: Thymeleaf templates served by a controller (WebController).
  - API layer: REST controllers returning JSON (HelloRestController, GoodbyRestController).
- No database or persistent storage is present — this is a stateless demo that returns static/dynamic JSON messages.

How the main application class wires things together
- The entry point is Hackathon2025Application.java annotated with @SpringBootApplication; this triggers component scanning and auto-configuration.
- Controllers are simple Spring components (@Controller and @RestController) and are auto-wired by Spring without additional configuration.

Request flow (end-to-end)
- Browser → HTTP GET "/" → WebController#index → returns "index" view name → Thymeleaf renders templates/index.html with model attributes (title).
- Browser → JavaScript fetch → GET "/api/hello" (or other /api/* endpoints) → corresponding @RestController method produces Map<String,String> → Spring converts it to JSON and returns in the HTTP response → JavaScript processes the JSON and updates the DOM.

## 3. Components and Responsibilities

Main Java classes
- Hackathon2025Application
  - Spring Boot entry point. Starts the embedded server and loads configuration.
- WebController
  - Annotated with @Controller.
  - Handles GET "/" and adds "title" to the model; returns the "index" template.
- HelloRestController
  - Annotated with @RestController.
  - GET /api/hello → returns { "message": "Hello again and again from REST API for Hackathon 2025!" }
  - GET /api/hello2 → returns a dummy message for hello2
  - GET /api/hello3 → returns a dummy message for hello3
- GoodbyRestController
  - Annotated with @RestController.
  - GET /api/goodby?name={name} → returns a message "Goodbye, {name}, from REST API for Hackathon 2025!!!!"
    - Query parameter "name" has defaultValue "Gast" when absent.
  - GET /api/goodnight → returns a good night message

Overview of REST endpoints (paths and responses)
- GET /api/hello
  - Response: JSON { "message": "Hello again and again from REST API for Hackathon 2025!" }
- GET /api/hello2
  - Response: JSON { "message": "Dummy text for hello2" }
- GET /api/hello3
  - Response: JSON { "message": "Another dummy text for hello3" }
- GET /api/goodby?name=...
  - Response: JSON { "message": "Goodbye, {name}, from REST API for Hackathon 2025!!!!" }
  - Query param: name (defaults to "Gast")
- GET /api/goodnight
  - Response: JSON { "message": "Good night from REST API for Hackathon 2025!!!" }

Overview of HTML pages and purpose
- templates/index.html
  - Simple landing page served at "/".
  - Shows the title (from model attribute "title") and a button "Test REST" that triggers JS to call /api/hello and display the returned JSON in the page.
- templates/followup.html
  - A more comprehensive manual test / demo page that includes buttons to call /api/hello, /api/hello2, /api/hello3 and /api/goodby (with input) and /api/goodnight.
  - Each button triggers a client-side fetch and places the JSON result into an element on the page for inspection.

## 4. UI and REST Interaction

Index page behavior
- The index page renders the title provided by WebController.
- The page includes a JavaScript function callApi() that does:
  - fetch('/api/hello')
  - parse the JSON response
  - write the JSON (stringified) into the element with id "apiResult"
- Example of the client-side fetch used on index:
  - async function callApi() { const res = await fetch('/api/hello'); const j = await res.json(); ... }

Followup page behavior
- followup.html exposes buttons for each API endpoint and a text input for the /api/goodby call.
- Each button calls an async function such as callHello(), callHello2(), callHello3() which fetch the corresponding endpoint and display the results.
- callGoodby() reads the value from the input field, encodes it, and calls /api/goodby?name=... to include the user-provided name.

How UI interacts with REST controllers
- The UI performs client-side HTTP GET requests (fetch) to the REST endpoints. The controllers return Map<String,String> values that Spring serializes into JSON.
- No CSRF tokens, authentication, or form POSTs are used — the interaction is simple GET-based demo traffic.

## 5. Testing Strategy

Unit and integration tests
- The project uses JUnit for unit tests (standard approach in Spring Boot projects).
- Some unit tests in the repository are generated with the help of Azure OpenAI in automated workflows (per project automation). These focus on verifying controller responses and simple wiring.

UI and API tests with Playwright
- Playwright is used for end-to-end browser and API testing. Playwright scripts exercise the UI buttons (index and followup) and verify that the expected JSON is shown on the page.
- Playwright can also be used to call the REST endpoints directly and assert the JSON responses.

What is covered (high-level)
- Controller endpoints return expected JSON structure and content.
- UI behavior: clicking "Test REST" triggers a fetch and displays the response.
- followup.html demonstrates more flows (including query parameter handling).
- The tests exercise the demo contract (endpoints and UI) rather than complex business logic.

Note: This summary is based on the existing controllers/templates. Exact test names and assertions may vary; generated tests aim to cover the above interactions.

## 6. CI/CD and AI-Assisted Workflows

GitHub Actions workflows (project conventions)
- The repository contains GitHub Actions that:
  - generate or update JUnit tests for Java code using Azure OpenAI,
  - generate or update Playwright UI/API tests using Azure OpenAI,
  - generate or refresh architecture/documentation files (including this file),
  - run Maven build and tests and execute Playwright tests as part of CI.
- Generated artifacts (tests, docs) are committed back to the pull request branch, not directly to main. This enables human review of generated changes before merging.

Important note: This architecture document itself was produced by an AI-assisted workflow and should be reviewed and refined by humans. Automated test generation accelerates coverage but must be validated for correctness, reliability, and security.

Assumption: The repository’s workflows are configured to run Playwright and Maven in CI and to use Azure OpenAI for generation tasks as described.

## 7. Limitations and Next Steps

Current limitations
- No persistence layer: there is no database or repository abstraction — controllers return static or simple dynamic text.
- No service layer: controller logic is directly in controllers; this limits separation of concerns.
- Minimal input validation and error handling: e.g., /api/goodby relies on a simple query parameter and does not validate inputs.
- No security: no authentication/authorization or CSRF protection is present (suitable for a demo but not production).
- Limited configuration and observability: no centralized config profiles, metrics, or structured logging beyond default behavior.

Suggested next steps
- Introduce a service layer (e.g., HelloService, GoodbyService) to decouple controller logic and make unit testing easier.
- Add DTOs and response models instead of Map<String,String> for clearer schemas.
- Add input validation (Spring @Valid, DTO constraints) and consistent error handling (ControllerAdvice).
- Add tests for negative/error cases and edge conditions.
- Add logging and metrics, and externalize messages/configuration to properties.
- If persistence is required, add Spring Data repositories and an embedded DB for integration tests.
- Harden CI: add dependency scanning, static analysis, and review rules for AI-generated commits.

Appendix — small code references
- Entry point:
  - @SpringBootApplication public class Hackathon2025Application { public static void main(String[] args) { SpringApplication.run(...); } }
- Example REST mapping:
  - @GetMapping("/api/hello") public Map<String,String> hello() { return Map.of("message","Hello..."); }

If you have questions about any controller, test, or the CI configuration files, point me to the specific file(s) and I will expand or refine this document.
