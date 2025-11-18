#!/usr/bin/env python3
"""
generate_ui_tests_with_azure_openai.py

Erzeugt EIN Playwright-Testfile für:

- Die Startseite (GET /, index.html) – UI-Test mit Button und REST-Aufruf
- Alle REST-Endpoints unter /api/... – API-Tests via Playwright request

Strenge Regeln:
- Keine erfundenen Routen oder Seiten
- Nur Routen testen, die klar aus den Controllern hervorgehen
- Nur Titel testen, wenn im Template explizit ein <title> steht
- Keine verrückten String-Tricks wie .replace(' ', '') zum Vergleichen

Erwartet Umgebungsvariablen:
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT
"""

import os
import pathlib
import textwrap
import json
import requests
import re

API_VERSION = "2024-02-15-preview"  # ggf. anpassen


def read_file(path: pathlib.Path) -> str:
    if not path.exists():
        print(f"[WARN] Datei nicht gefunden: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def call_azure_openai_for_playwright(prompt: str) -> str:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    system_prompt = (
        "You are a senior test engineer specialized in web UIs and Playwright. "
        "You write high-quality, compilable Playwright tests in TypeScript "
        "using '@playwright/test'. Tests must focus on realistic user flows "
        "and robust validation checks. You do NOT invent endpoints or pages. "
        "You NEVER rely on fragile exact strings when a looser regex or "
        "substring check suffices."
    )

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        # kein max_tokens / keine temperature → Azure-kompatibel
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=90)
    if resp.status_code >= 400:
        raise RuntimeError(f"Azure OpenAI Fehler {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def strip_code_fences(text: str) -> str:
    """
    Entfernt ```ts``` / ```typescript``` / ```js``` Codeblöcke, falls vorhanden.
    """
    match = re.search(r"```(?:ts|typescript|javascript|js)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def collect_controllers(controllers_dir: pathlib.Path):
    """
    Sammelt alle *.java-Dateien unterhalb des Controllers-Verzeichnisses.
    Rückgabe: Liste von Dicts mit {name, path, code}.
    """
    result = []
    for path in controllers_dir.rglob("*.java"):
        code = read_file(path)
        result.append(
            {
                "name": path.name,
                "path": str(path),
                "code": code,
            }
        )
    return result


def get_index_html(templates_dir: pathlib.Path) -> str:
    """
    Sucht index.html (oder ähnliches) und gibt den Inhalt zurück.
    """
    for path in templates_dir.rglob("index.html"):
        return read_file(path)
    # Fallback: irgendein Template
    for path in templates_dir.rglob("*.html"):
        return read_file(path)
    return ""


def build_prompt(controllers, index_html: str) -> str:
    controllers_str = ""
    for c in controllers:
        controllers_str += f"\nController {c['name']} (Pfad: {c['path']}):\n```java\n{c['code']}\n```\n"

    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    There is an index page (GET /) rendered via a Thymeleaf template, and there are
    REST endpoints implemented in Spring controllers, especially under /api/... paths.

    Your job is to generate ONE Playwright test file in TypeScript named
    `ui-hackathon2025.spec.ts` that contains:

    1) A UI test for the index page (GET /)
    2) API tests for all REST endpoints whose path clearly starts with /api/
       and that return JSON.

    === INDEX PAGE BEHAVIOR (MUST BE STABLE) ===

    The index.html currently looks like this (simplified):

    ```html
    {index_html}
    ```

    The intended behavior for GET / is:

    - GET / returns the main page.
    - The <title> contains the word "Hackathon".
    - The main <h1> heading contains "Hackathon 2025 Demo".
    - There is a button with the text "Test REST" that calls the JavaScript function callApi().
    - There is a <p id="apiResult"></p> element.
      On initial load, #apiResult exists in the DOM, but its text content is an empty string.
    - When the user clicks the "Test REST" button:
        - The browser calls fetch('/api/hello').
        - The response is JSON.
        - document.getElementById('apiResult').innerText is set to JSON.stringify(json).
        - After the click, #apiResult contains a non-empty JSON string that should contain
          a 'hello' message.

    For this, you MUST include a test with the EXACT name:
      "hackathon2025 UI: initial render and REST interaction"

    Its structure MUST closely follow this pattern:

    ```ts
    import {{ test, expect }} from '@playwright/test';

    test('hackathon2025 UI: initial render and REST interaction', async ({{ page }}) => {{
      await page.goto('http://localhost:8080/');
      expect(await page.title()).toContain('Hackathon');
      const heading = page.getByRole('heading', {{ level: 1 }});
      await expect(heading).toContainText('Hackathon 2025 Demo');
      const button = page.getByRole('button', {{ name: 'Test REST' }});
      await expect(button).toBeVisible();
      const apiResult = page.locator('#apiResult');
      const count = await apiResult.count();
      expect(count).toBeGreaterThan(0);
      await expect(apiResult).toHaveText('');
      await button.click();
      await expect(apiResult).not.toHaveText('', {{ timeout: 5000 }});
      const raw = await apiResult.innerText();
      const parsed: any = JSON.parse(raw);
      expect(parsed).not.toBeNull();
      expect(typeof parsed).toBe('object');
      expect(Object.keys(parsed).length).toBeGreaterThan(0);
      expect(raw.toLowerCase()).toContain('hello');
    }});
    ```

    Only adapt selectors or expected texts IF the provided HTML has clearly changed.

    === CONTROLLERS AND REST ENDPOINTS ===

    Here are all Java controllers:

    {controllers_str}

    From these controllers, you must:

    - Identify all REST endpoints (e.g. methods annotated with @GetMapping, @PostMapping, @RequestMapping)
      whose path clearly starts with '/api/'.
    - For each such endpoint that returns JSON, create a dedicated API test in the SAME file
      (ui-hackathon2025.spec.ts).

    For API tests:

    - Use Playwright's APIRequestContext via the `request` fixture:
        test('...', async ({{ request }}) => {{ ... }})
    - For each /api/... endpoint:
        - Perform a GET request (or the appropriate HTTP method) to
          'http://localhost:8080<path>'.
        - Assert that the status is 200.
        - Parse the JSON body.
        - Assert that the parsed value is an object and has at least one field.
        - If the controller clearly uses a hard-coded message like
          "Hello from rest api for hackathon 2025!!!", you may:
            - assert that `String(message).toLowerCase()` contains 'hello'
        - If the controller clearly uses a message like
          "good night from rest api for hackathon 2025!!!", you may:
            - assert that `String(message).toLowerCase()` matches `/good\\s+night/`.
        - DO NOT use tricks like `'good night'.replace(' ', '')` or similar.
        - DO NOT assert on exact full strings unless absolutely necessary.
          Prefer robust checks (contains, regex with optional whitespace).

    Very important RULES:

    - DO NOT invent any endpoints or routes.
      If there is no controller method annotated with a given path, IGNORE it.
    - DO NOT invent any pages like "/followup" or titles like "Followup Demo"
      if they are not clearly present in the controllers and templates.
    - Only assert on <title> if the template clearly contains a <title> element.
      Otherwise, skip title checks for that page.
    - Keep test names descriptive but simple, e.g.:
        test('hackathon2025 API: /api/hello returns JSON', ...)
        test('hackathon2025 API: /api/goodbye returns JSON', ...)
    - All tests must be in a single file:
        ui-hackathon2025.spec.ts
    - Use:
        import {{ test, expect }} from '@playwright/test';

    Output ONLY the TypeScript code of ui-hackathon2025.spec.ts (no explanations, no comments).
    """)


def main():
    # Skript liegt in scripts/, Repo-Root ist eine Ebene höher
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    controllers_dir = repo_root / "src/main/java/com/example/hackathon2025"
    templates_dir = repo_root / "src/main/resources/templates"

    controllers = collect_controllers(controllers_dir)
    index_html = get_index_html(templates_dir)

    if not controllers:
        print(f"[WARN] Keine Controller unter {controllers_dir} gefunden.")
    if not index_html:
        print(f"[WARN] Kein index.html unter {templates_dir} gefunden.")

    prompt = build_prompt(controllers, index_html)

    print("[INFO] Rufe Azure OpenAI zur Generierung von Playwright-Tests auf...")
    completion = call_azure_openai_for_playwright(prompt)
    ts_code = strip_code_fences(completion)

    tests_dir = repo_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    target_path = tests_dir / "ui-hackathon2025.spec.ts"
    target_path.write_text(ts_code, encoding="utf-8")

    print(f"[OK] Playwright UI-Test geschrieben: {target_path}")


if __name__ == "__main__":
    main()
