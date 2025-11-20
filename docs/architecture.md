<!--
  This document was initially generated automatically (Azure OpenAI and/or static analysis).
  Please review and adapt it as needed.
-->

# hackathon2025 — Architecture and Technical Documentation

Version: initial demo  
Location: docs/architecture.md

## 1. Introduction

This document describes the architecture and technical details of the `hackathon2025` Spring Boot demo application. It is intended to help new developers quickly understand the project structure, responsibilities of components, how the UI and REST APIs interact, how to test the application, and practical CI/CD and AI-assisted development suggestions. All descriptions are based on the Java controllers and Thymeleaf templates included in the repository.

Assumptions:
- The project is a Spring Boot application (main class `Hackathon2025Application`).
- The build system (Maven or Gradle) and CI configurations are not included in the provided sources; recommended approaches are suggested in the CI/CD section.

## 2. Architecture Overview

hackathon2025 is a small monolithic Spring Boot web application that exposes a set of REST endpoints and serves HTML pages rendered with Thymeleaf. Key characteristics:

- Layering: Controllers (web and REST) directly serve responses — the project is controller-centric and does not currently include service or repository layers.
- UI: Thymeleaf templates (`index.html`, `followup.html`) are used for simple client-side interactions and call the REST API endpoints via fetch().
- API: Multiple lightweight REST controllers provide JSON responses under the `/api/*` path.
- Statelessness: All controllers are essentially stateless. Immutable maps and simple computation are used to build responses.

Logical diagram (textual):
- Browser (index.html / followup.html)
  -> HTTP GET/JS fetch -> REST Controllers (/api/*)
  -> Response: JSON
- Spring Boot application (embedded container serving static/templated pages + REST controllers)

## 3. Components and Responsibilities

Files of interest and their responsibilities:

- `Hackathon2025Application.java`
  - Spring Boot application entry point. Starts the embedded server and application context.

- REST Controllers (return JSON via `@RestController`):
  - `HelloRestController`
    - Endpoints:
      - GET `/api/hello` — returns a greeting message.
      - GET `/api/hello2` — returns a dummy text.
      - GET `/api/hello3` — returns another dummy text.
  - `Hello2RestController`
    - Endpoint:
      - GET `/api/hello2alt` — alternative hello message.
  - `GoodbyRestController`
    - Endpoints:
      - GET `/api/goodby?name=<name>` — returns a goodbye message. If `name` omitted, defaults to `"Gast"`.
      - GET `/api/goodnight` — returns a short message.
  - `NatureImageRestController`
    - Endpoint:
      - GET `/api/nature-image?keyword=<keyword>` — returns a JSON object containing the requested keyword and an image URL.
    - Implementation notes:
      - Contains an immutable map of keyword -> list of image URLs (external picsum.photos links).
      - If keyword is not found, returns a default seed-based picsum URL.
      - Picks a random URL from the list on each request.
  - `FibonacciRestController`
    - Endpoint:
      - GET `/api/fibonacci?number=<n>` — returns the requested number and its Fibonacci value (computed iteratively).
    - Implementation notes:
      - Negative numbers return an error JSON: `{"error":"Die Zahl muss >= 0 sein."}`
      - The Fibonacci calculation is iterative and returns `long`.

- Web Controller:
  - `WebController`
    - Maps GET `/` to Thymeleaf template `index.html`. Adds a `title` model attribute.

- Thymeleaf templates:
  - `templates/index.html`
    - Landing page that uses JavaScript to call `/api/hello` and `/api/nature-image` and to display returned data (images and messages).
  - `templates/followup.html`
    - A demo page to invoke the hello and goodby endpoints using client-side fetch() and display JSON responses.

Implementation style notes:
- Controllers widely use `Map.of(...)` to construct small JSON responses.
- Endpoints are all GET operations and rely on query params for input.
- There is no persistence or external service integration except fetching images via URLs in the frontend.

## 4. UI and REST Interaction

The UI is thin client-side JavaScript embedded in Thymeleaf pages. Interaction patterns:

- index.html
  - `callApi()` calls `/api/hello` and displays the JSON in a `<p>`.
  - `showNatureImage(keyword)` calls `/api/nature-image?keyword=...` and uses the returned `imageUrl` to set an `<img>` src and display it.
  - If no keyword provided by user, shows a simple alert.

- followup.html
  - Buttons call `/api/hello`, `/api/hello2`, `/api/hello3`.
  - Provides an input to call `/api/goodby?name=...` and displays JSON.

Typical example curl requests (useful to test APIs directly):
- GET hello:
  curl -s http://localhost:8080/api/hello
- GET nature image:
  curl -s "http://localhost:8080/api/nature-image?keyword=tree"
- GET fibonacci:
  curl -s "http://localhost:8080/api/fibonacci?number=10"

Notes on UX and behavior:
- Client-side code assumes JSON responses and updates the DOM accordingly.
- No client-side error handling beyond basic alerts; e.g. network errors or non-200 responses are not handled explicitly.

## 5. Testing Strategy

Current repository does not include tests (assumption). Recommended testing approach:

Unit testing:
- Test pure logic methods (e.g., `calculateFibonacci`) with JUnit.
- Example unit test assert patterns: `assertEquals(55, calculateFibonacci(10));`

Controller tests:
- Use MockMvc (Spring MVC test) to assert endpoint status codes, default parameter behavior, and JSON payloads.
- Example MockMvc pseudo-code:
  - mockMvc.perform(get("/api/goodby")) -> expect status 200 and JSON `message` contains "Gast".
  - mockMvc.perform(get("/api/fibonacci").param("number","-1")) -> expect JSON error message.

Integration / end-to-end:
- Boot the application context and perform requests to verify template rendering and REST endpoints together.
- Use a headless browser or Playwright/Cypress/Selenium to verify the client-side fetch flows:
  - Buttons on `index.html` correctly trigger image updates.
  - `followup.html` buttons show JSON in the page.

Test data and edge cases:
- Fibonacci for large inputs (overflow risk for long).
- Nature-image unknown keywords — verify fallback behavior.
- Concurrent access to endpoints (load tests) to spot thread-safety or performance issues.

## 6. CI/CD and AI-Assisted Workflows

CI/CD recommendations (no pipeline present in repo — assumption):
- Pipeline stages:
  1. Build (Maven/Gradle)
  2. Unit tests and integration tests
  3. Static analysis (SpotBugs, PMD, Checkstyle)
  4. Dependency vulnerability scan (OWASP Dependency-Check)
  5. Build artifact / container image
  6. Deploy to staging, then production with approvals
- Example for GitHub Actions: use a workflow that runs `./mvnw -B verify` or `./gradlew check` and then builds a Docker image.

AI-assisted workflows:
- Use AI tools to generate:
  - Unit tests and MockMvc tests from controller signatures.
  - Small refactors suggestions (e.g., replace Random with ThreadLocalRandom).
  - Draft API documentation and OpenAPI spec.
- Recommended guardrails:
  - Always review and run generated code locally.
  - Use AI output as a starting point (not authoritative).
  - Include human review for security-sensitive changes.

Suggested automation tasks:
- Auto-generate OpenAPI/Swagger from controllers using springdoc-openapi.
- Use Dependabot or Renovate for dependency updates.
- Auto-generate release notes from merged PRs.

## 7. Limitations and Next Steps

Known limitations (based on current sources):
- No authentication/authorization or security controls.
- All endpoints are GET-only and accept query parameters; no DTOs, validation annotations, or centralized error handling.
- No tests or CI/CD configs shipped with the demo (assumption).
- No logging, metrics, or health endpoints present.
- Fibonacci uses `long` and may overflow for large numbers; no mitigation or input bounds.

Suggested next steps (non-invasive, prioritized):
1. Add tests:
   - Unit tests for Fibonacci method and other logic.
   - Controller tests using MockMvc.
2. Add basic input validation and error handling:
   - Use @Validated, DTOs, and GlobalExceptionHandler to return consistent error formats.
3. Improve randomness and performance:
   - Consider ThreadLocalRandom for the image selection.
4. API Documentation:
   - Integrate springdoc-openapi to expose an OpenAPI spec and Swagger UI.
5. Observability and security:
   - Add logging (SLF4J), health checks (actuator), and simple auth for protected endpoints.
6. CI/CD:
   - Add a GitHub Actions pipeline with build, test, static analysis and containerization steps.
7. Frontend improvements:
   - Add robust error handling in the client JS (handle non-200 responses) and unit tests for scripts.
8. Production readiness:
   - Rate limiting and input sanitization, content security headers, and container image scanning.

If you want, I can produce:
- Example MockMvc test classes for the controllers.
- A starter GitHub Actions workflow file.
- A small refactor PR that extracts Fibonacci into a service, adds validation, and a few unit tests.

End of document.

## Related Work Items

- **Pull Request:**
  - Title: Update HelloRestControllerTest.java

