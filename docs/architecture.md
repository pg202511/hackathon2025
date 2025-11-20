<!--
  This document was initially generated automatically (Azure OpenAI and/or static analysis).
  Please review and adapt it as needed.
-->

# hackathon2025 — Architecture and Technical Documentation

This document describes the architecture, components, interactions, testing strategy and recommended CI/CD and AI-assisted workflows for the hackathon2025 Spring Boot demo application. It is intended to help new developers quickly understand the project and make safe extensions.

## 1. Introduction

hackathon2025 is a small Spring Boot web application that demonstrates:
- A main Spring Boot application entry-point.
- Several REST controllers exposing simple JSON endpoints.
- A Thymeleaf-based HTML UI that consumes the REST APIs via client-side fetch calls.

The codebase is intentionally compact and focused on demo functionality (greeting endpoints, a Fibonacci calculator, and a small nature-image demo). It is a good basis for learning Spring Web, REST, and simple front-end integration.

Assumption: There is no existing CI/CD or automated test configuration in the repository; recommendations in this document are proposals.

## 2. Architecture Overview

High-level structure:
- Spring Boot application (com.example.hackathon2025).
- Controllers expose REST endpoints under `/api/*` and a single MVC controller mapping `/` to a Thymeleaf template.
- Front-end templates are server-side Thymeleaf (templates/index.html and templates/followup.html) but rely on browser-side JavaScript (fetch) to call REST endpoints and update the DOM.

Runtime behavior:
- Application starts with Hackathon2025Application (standard Spring Boot main class).
- REST controllers handle HTTP GET requests and return JSON Maps. No explicit service or repository layers exist — controllers contain the logic.
- Thymeleaf renders initial HTML pages; runtime interactions (button clicks) are implemented with fetch() calls to the REST endpoints.

Core concerns demonstrated:
- HTTP routing and JSON REST responses.
- Simple parameter handling (e.g., `@RequestParam`).
- Minimal server-rendered HTML with client-side interaction.

## 3. Components and Responsibilities

Package: com.example.hackathon2025

Primary Java classes:
- Hackathon2025Application.java
  - Standard Spring Boot application bootstrap.

- HelloRestController.java
  - REST endpoints:
    - GET /api/hello
    - GET /api/hello2
    - GET /api/hello3
  - Returns simple message Maps (used for demo and UI tests).

- GoodbyRestController.java
  - REST endpoints:
    - GET /api/goodby?name={name} (default "Gast")
    - GET /api/goodnight
  - Demonstrates `@RequestParam` and string composition.

- NatureImageRestController.java
  - REST endpoint:
    - GET /api/nature-image?keyword={keyword}
  - Maintains an in-memory Map of keywords -> image URL lists (picsum.photos).
  - On request, selects a random image URL for the given keyword and returns JSON containing `keyword` and `imageUrl`.

- FibonacciRestController.java
  - REST endpoint:
    - GET /api/fibonacci?number={number}
  - Validates number (non-negative) and returns the nth Fibonacci value computed iteratively.
  - Returns error JSON if input is invalid.

- WebController.java
  - MVC controller returning Thymeleaf template `index` for path `/`.
  - Injects model attribute `title` used by the template.

Templates:
- templates/index.html
  - Main UI: shows title, a "Test REST" button to call /api/hello, and a nature-image search UI that calls `/api/nature-image`.
  - Uses fetch() to request JSON and updates DOM (`img.src` etc).

- templates/followup.html
  - Demo page with buttons to invoke Hello and Goodby controllers and display returned JSON.

Design observations:
- Controllers return Map instances (quick demo-friendly JSON). No DTO classes.
- No persistent storage or service layer; logic is embedded in controllers.
- No security, validation frameworks, exception handlers, or logging are present.

## 4. UI and REST Interaction

Client-side interactions are implemented with fetch-based JavaScript in templates.

Example pattern used (index.html / followup.html):
- Fetch an endpoint and parse JSON:
  - const res = await fetch('/api/hello'); const j = await res.json();
- Update DOM elements:
  - document.getElementById('apiResult').innerText = JSON.stringify(j);

Available REST endpoints (summary):
- GET /api/hello
- GET /api/hello2
- GET /api/hello3
- GET /api/goodby?name={name}
- GET /api/goodnight
- GET /api/nature-image?keyword={keyword}
- GET /api/fibonacci?number={number}

Example curl to call Fibonacci:
- curl 'http://localhost:8080/api/fibonacci?number=10'
Response (example): {"number":10,"fibonacci":55}

Notes:
- The UI is purely client-driven once the page loads — no WebSocket or server push.
- Image URLs are external (picsum.photos); images are loaded directly by the browser.

## 5. Testing Strategy

Given the small size, adopt a layered test approach:

Unit tests
- Use JUnit 5 and Spring's MockMvc for controller unit tests.
- Focus on: correct status codes, JSON structure, parameter handling, and edge cases (e.g., negative Fibonacci number).
- Example assertions:
  - GET /api/goodby without name uses "Gast".
  - GET /api/fibonacci with negative number returns error key.

Integration tests
- Use @SpringBootTest with TestRestTemplate (or MockMvc with webEnvironment) to exercise real serialization and template rendering.
- Validate Thymeleaf pages contain expected elements and that client endpoints return JSON.

End-to-end / UI tests
- Optional: Selenium/WebDriver tests to simulate clicking buttons on index.html and verifying image appears or JSON is displayed.
- Alternatively, lightweight headless browser tests (Playwright) that assert the DOM update logic.

Suggested test cases
- nature-image: keyword not present -> returns seed URL.
- Fibonacci: check boundary values (0,1,2) and moderate numbers for performance (e.g., 50).
- Goodby: verify default and custom `name` parameter behavior.

Test automation best practices
- Run all tests in CI on every PR.
- Keep tests deterministic — mock randomization when needed (e.g., inject Random or use deterministic seed).

## 6. CI/CD and AI-Assisted Workflows

CI/CD (recommended / assumed)
- Although no pipeline files are present, a minimal GitHub Actions pipeline is recommended:
  - Steps: checkout, set up JDK, mvn -B -DskipTests=false verify, build Docker image, push artifact/image on release branch.
- Add policy: run unit tests, static analysis (SpotBugs, Checkstyle), and integration tests.

Sample minimal GitHub Actions step (proposal):
- name: Build and test
  run: mvn -B -DskipTests=false verify

Deployment suggestions
- Containerize with a simple Dockerfile (maven build + JRE image) and push to a registry.
- Deploy to any cloud platform (Heroku, AWS ECS, GCP Cloud Run) as a stateless service.

AI-Assisted Workflows
- Use AI tools to accelerate:
  - Generate unit/integration test scaffolding for controllers.
  - Create PR descriptions and changelogs from commit diffs.
  - Suggest refactorings (e.g., extracting service layer, adding DTOs).
  - Auto-generate API documentation (OpenAPI/Swagger) from code annotations (quick stub generation).
- Apply human review to AI outputs; treat them as suggestions and verify correctness.

Security and compliance
- Integrate automated dependency scanning (e.g., Dependabot, Snyk) into CI.
- Use static analysis and code scanning tools as part of the pipeline.

## 7. Limitations and Next Steps

Current project limitations (observed in code)
- No service/repository separation — controllers contain logic (Fibonacci, image selection).
- No global error handling (e.g., @ControllerAdvice). Controllers return Map with "error" key — not standardized HTTP error responses.
- No validation framework for inputs beyond simple checks in controller.
- No authentication/authorization or rate limiting.
- No structured logging or observability (metrics/tracing).
- Fibonacci uses long and can overflow for large n; no bounds checking or protection.
- External image URLs are fetched directly by the browser (no caching/proxying).
- No CI/CD or infrastructure-as-code included in repo (assumption).

Recommended next steps (prioritized)
1. Introduce a service layer: move Fibonacci and image selection into services and add unit tests for them.
2. Add standardized error handling with @ControllerAdvice and proper HTTP status codes.
3. Add basic input validation (Spring Validation) and guardrails for expensive operations (limit max Fibonacci n).
4. Add logging and simple health endpoints (Actuator) for production readiness.
5. Add OpenAPI/Swagger annotations for API documentation and generate interactive docs.
6. Implement CI pipeline (GitHub Actions) to run tests, static analysis, and produce artifacts.
7. Add basic security (spring-boot-starter-security) if endpoints become non-demo and need protection.

Assumption: The repository is primarily a demo; the suggested next steps move it towards production-quality architecture while preserving the current demo behavior.

---

If you need, I can:
- Provide example unit test stubs for each controller using MockMvc.
- Provide a starter GitHub Actions workflow and Dockerfile.
- Propose a refactor plan to extract services and add proper error handling.

## Related Work Items

- **Pull Request:**
  - Title: doc generator changed 2
  - Description:

    added jira issue link

