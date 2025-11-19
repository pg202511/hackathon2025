<!--
  This document was initially generated with the help of Azure OpenAI.
  Please review and adapt it as needed.
-->

# Architecture and Technical Overview — hackathon2025

This document describes the structure, responsibilities, and runtime behavior of the hackathon2025 demo Spring Boot application. It is intended to help new developers quickly understand the codebase, how the pieces interact, what is covered by tests, and what reasonable next steps are.

Important note: this document was produced by an AI-assisted workflow and should be reviewed and adjusted by project maintainers for accuracy and style.

## 1. Introduction

What the application does
- hackathon2025 is a small demo web application that exposes several REST endpoints and a simple Thymeleaf-based UI.
- The UI contains two HTML templates:
  - index.html — a landing page with a "Test REST" button that calls the `/api/hello` endpoint.
  - followup.html — a more interactive page providing buttons to call several REST endpoints (hello/hello2/hello3, goodby, goodnight).
- REST endpoints return JSON maps with small text messages or computed values (the Fibonacci endpoint).

Main technologies
- Java 11+ (standard Spring Boot Java application).
- Spring Boot (spring-boot-starter-web and spring-boot-starter-thymeleaf implied).
- Thymeleaf for server-side HTML templating.
- Browser-side JavaScript uses fetch() to call REST endpoints.
- CI/CD and test generation workflows use Azure OpenAI to generate tests (unit and Playwright UI/API tests) and GitHub Actions to run them (see CI/CD section).

## 2. Architecture Overview

High-level architecture
- Single Spring Boot application containing:
  - REST controllers that expose /api/** endpoints.
  - A Web controller that returns Thymeleaf templates for UI pages.
  - Server-side templates under `resources/templates` (index.html, followup.html).
- No persistence layer, no database, and no external services are used in the current codebase — it is a self-contained demo.

How the main application class wires things together
- The entry point is Hackathon2025Application annotated with @SpringBootApplication and a standard SpringApplication.run(...). Component scanning picks up controllers and Thymeleaf auto-configuration to serve templates.

Request flow (typical)
- Browser → HTTP GET / → WebController#index returns the "index" view name → Thymeleaf renders `index.html` with model attributes.
- Browser-side JavaScript uses fetch() to call REST endpoints (e.g., GET /api/hello).
- Spring MVC dispatches fetch request to the matching @RestController method which returns a Map<String,?>. Spring Boot automatically converts the Map to JSON in the response.

## 3. Components and Responsibilities

Main classes (controllers)
- Hackathon2025Application
  - Application bootstrap class — starts the Spring context.
- WebController
  - A @Controller that maps GET "/" and adds a model attribute `title` = "Hackathon 2025 Demo", then returns "index".
- HelloRestController
  - @RestController exposing:
    - GET /api/hello → Map with message "Hello again and again from REST API for Hackathon 2025!"
    - GET /api/hello2 → Map with message "Dummy text for hello2"
    - GET /api/hello3 → Map with message "Another dummy text for hello3"
- GoodbyRestController
  - @RestController exposing:
    - GET /api/goodby?name=... → Map with message "Goodbye, <name>, from REST API for Hackathon 2025!!!!"
      - default name = "Gast"
    - GET /api/goodnight → Map with message "Good night from REST API for Hackathon 2025!!!"
- FibonacciRestController
  - @RestController exposing:
    - GET /api/fibonacci?number=N → returns a Map with the original `number` and a `fibonacci` value (computed iteratively).
    - If `number < 0` the controller returns Map with an `"error"` key and a German error message: "Die Zahl muss >= 0 sein."

Notes on responsibilities
- Controllers return simple Map instances; there are no DTO classes, service layers, or repositories.
- Fibonacci calculation uses an iterative approach (loop from 2 to n) to compute the nth Fibonacci number.

REST endpoints summary
- /api/hello, /api/hello2, /api/hello3 — simple message responses.
- /api/goodby — accepts query param `name` (defaults to "Gast") and returns a custom message.
- /api/goodnight — simple goodnight message.
- /api/fibonacci — accepts query param `number` (default 0), returns computed Fibonacci number or an error.

HTML templates overview
- index.html
  - Displays the title (injected from the model).
  - Has a "Test REST" button that triggers a client-side fetch to `/api/hello` and writes the JSON result into the page.
- followup.html
  - Contains multiple buttons and inputs to exercise `/api/hello*`, `/api/goodby`, `/api/goodnight`.
  - Results are displayed in <p> tags by updating innerText with the returned JSON string.

Important implementation detail (assumption)
- The repository contains `followup.html` under templates, but the only explicit WebController mapping in the provided code is for "/", which returns "index". There is no controller method mapping to render `followup.html` in the shown code. It may be intended to be served via an additional controller or a direct route (not present). This is an explicit assumption to highlight.

## 4. UI and REST Interaction

Index page behavior
- Button labeled "Test REST" invokes client-side JavaScript function `callApi()`.
- callApi() does:
  - fetch('/api/hello') → await response → parse JSON → write JSON.stringify(result) to element id `apiResult`.
- Example of returned payload from GET /api/hello:
  - { "message": "Hello again and again from REST API for Hackathon 2025!" }

Followup page behavior
- Buttons each call functions that fetch the corresponding REST endpoints.
- For /api/goodby, the page reads the content of input `goodbyInput` and attaches it as query parameter `name`.
- Returned JSON is displayed as a raw string in the page (no client-side validation/formatting beyond JSON.stringify).

How UI interacts with controllers
- All UI-to-server interactions are via standard HTTP GET requests implemented using fetch().
- Responses are plain JSON produced by Spring Boot's message converters from Java Maps.
- No CSRF tokens, authentication, or complex headers are used in the demos.

## 5. Testing Strategy

What tests are present (project-level strategy)
- Unit tests:
  - Java unit tests use JUnit (typical for Spring Boot projects). Some unit tests are generated/updated by an Azure OpenAI-assisted workflow.
  - Unit tests typically assert controller behavior: expected JSON structure and values, default parameter handling, and error return for invalid inputs (e.g., negative Fibonacci).
- Playwright UI/API tests:
  - Browser-based automated tests simulate user interactions: loading pages, clicking "Test REST", filling the name input and pressing goodby buttons, and verifying that the UI updates with expected JSON responses.
  - Playwright tests are also generated/updated by Azure OpenAI workflows to cover the interactive flows.
- Coverage focus:
  - Key behaviors are covered: hello endpoints, goodby parameter default and interpolation, fibonacci calculation for valid and invalid inputs, and the primary UI flows that call these endpoints.

Note: The tests are generated by a GitHub Actions workflow (see next section) — generated tests are intended as a starting point and must be reviewed by developers.

## 6. CI/CD and AI-Assisted Workflows

GitHub Actions workflows in this repository perform the following (project policy / existing pipelines):
- Generate or update unit tests for Java controllers using Azure OpenAI (automated test generation).
- Generate or update Playwright UI/API tests using Azure OpenAI.
- Generate or update this architecture document (docs/architecture.md) using an AI workflow.
- Run Maven build and JUnit tests in CI.
- Run Playwright tests in a CI job that sets up a browser environment.
- When tests or docs are generated/updated, the workflow commits the generated artifacts back to the pull request branch (not directly to main). This keeps changes visible in PRs for human review.

Important: this architecture document itself was produced by an AI-assisted generation step in the CI flow — it should be reviewed and refined by humans before being accepted.

## 7. Limitations and Next Steps

Current limitations (observed from the code)
- Very small, demo-oriented codebase:
  - No service layer (business logic is in controllers).
  - No DTOs or validation framework (relying on default Spring parameter binding).
  - No persistence or configuration for storage.
  - No structured error responses / HTTP status codes beyond the default behavior.
  - followup.html exists but no explicit controller mapping in shown code (assumption noted above).
- Security is absent: no authentication, authorization or CSRF protections for interactive pages.
- No API documentation (OpenAPI/Swagger) or versioning.

Suggested next steps
- Add a service layer (e.g., FibonacciService, GreetingService) to move business logic out of controllers for testability and maintainability.
- Replace raw Map responses with DTO classes and explicit response types; use ResponseEntity to control HTTP status codes.
- Add validation (Spring Validation) for inputs and centralized exception handling (ControllerAdvice).
- Add API documentation (Springdoc/OpenAPI) and contract tests for the public API.
- Introduce automated integration tests and expand Playwright coverage to validate edge cases and error responses.
- Add logging, structured metrics, and basic security (e.g., OAuth2 or at least basic auth) if the app is extended beyond a demo.
- If followup.html should be reachable, add a controller mapping or navigation link from index to followup.

If you have questions about any specific file or want a checklist to onboard a new contributor (run, build, test), I can produce it as a follow-up.
