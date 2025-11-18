#!/usr/bin/env python3
"""
generate_ui_tests_with_azure_openai.py

Erzeugt ein Playwright-Testfile für ALLE relevanten Controller + HTML-Templates.

- Sammelt alle *Controller.java unter src/main/java
- Sammelt alle .html-Templates unter src/main/resources/templates
- Ruft Azure OpenAI auf, um ein TypeScript-Testfile zu generieren:
    tests/ui-hackathon2025.spec.ts

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
        "using '@playwright/test'. Tests must focus on realistic user flows, "
        "happy-path and basic validation checks. Do NOT explain anything; "
        "only output the TypeScript test file content."
    )

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        # kein max_tokens / keine temperature → kompatibel mit neueren Azure-Modellen
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
    Sammelt alle *Controller.java-Dateien unterhalb des angegebenen Verzeichnisses.
    Rückgabe: Liste von Dicts mit {name, path, code}.
    """
    result = []
    for path in controllers_dir.rglob("*Controller.java"):
        code = read_file(path)
        result.append(
            {
                "name": path.name,
                "path": str(path),
                "code": code,
            }
        )
    return result


def collect_templates(templates_dir: pathlib.Path):
    """
    Sammelt alle .html-Templates unterhalb des angegebenen Verzeichnisses.
    Rückgabe: Liste von Dicts mit {name, path, code}.
    """
    result = []
    for path in templates_dir.rglob("*.html"):
        code = read_file(path)
        result.append(
            {
                "name": path.name,
                "path": str(path),
                "code": code,
            }
        )
    return result


def build_prompt(controllers, templates) -> str:
    """
    Baut einen Prompt, der:
    - den bestehenden Index-Flow stabil hält
    - zusätzliche Tests für alle weiteren Controller/HTML-Seiten verlangt
    """

    # Für die Beschreibung der Index-Seite (falls vorhanden)
    index_html_snippet = ""
    for t in templates:
        if t["name"].lower().startswith("index."):
            index_html_snippet = t["code"]
            break

    controllers_str = ""
    for c in controllers:
        controllers_str += f"\nController {c['name']} (Pfad: {c['path']}):\n```java\n{c['code']}\n```\n"

    templates_str = ""
    for t in templates:
        templates_str += f"\nTemplate {t['name']} (Pfad: {t['path']}):\n```html\n{t['code']}\n```\n"

    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    The code base contains multiple Spring MVC controllers and multiple HTML (Thymeleaf) templates.
    Your job is to generate ONE Playwright test file in TypeScript that covers:

    - The main index page (GET /)
    - All other relevant routes and views that can be inferred from:
      - the controller mappings (@GetMapping, @RequestMapping, etc.)
      - the returned view names
      - the HTML templates under src/main/resources/templates

    The goal is:
    - to have at least one Playwright test for EVERY controller/view combination that renders a page,
    - verifying basic rendering (title, main heading, key buttons/links),
    - and invoking REST interactions when obvious (e.g. buttons that trigger fetch() calls).

    === CURRENT INDEX PAGE BEHAVIOR (must be preserved) ===

    The index.html currently looks like this (or very similar):

    ```html
    {index_html_snippet}
    ```

    The intended UI behavior for the index page is:

    - GET / returns the main page.
    - <title> should contain the word "Hackathon".
    - The main <h1> heading contains "Hackathon 2025 Demo".
    - There is a button with the text "Test REST" that calls the JavaScript function callApi().
    - There is a <p id="apiResult"></p> element.
      On initial load, #apiResult exists in the DOM, but its text content is an empty string.
    - When the user clicks the "Test REST" button:
        - The browser calls fetch('/api/hello').
        - The response is JSON.
        - document.getElementById('apiResult').innerText is set to JSON.stringify(json).
        - After the click, #apiResult contains a non-empty JSON string that should contain the word "Hello".

    You must include a test with the EXACT name:
      "hackathon2025 UI: initial render and REST interaction"
    that implements exactly this flow for GET /.

    Example structure for that first test (adapt it only if the HTML/behavior really changed):

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

    === ADDITIONAL CONTROLLERS AND HTML TEMPLATES ===

    Here are all controllers:

    {controllers_str}

    Here are all HTML templates:

    {templates_str}

    Your tasks for ADDITIONAL tests:

    1. Inspect all controllers (*Controller.java) and identify GET routes and view names
       (e.g. @GetMapping("/goodbye") returning "goodbye").

    2. Inspect the HTML templates and match them to controllers/views by name
       (e.g. a controller returns "goodbye" -> template goodbye.html or goodby.html).

    3. For each such page/view:
       - Add a dedicated Playwright test in the SAME file (ui-hackathon2025.spec.ts).
       - Name the test descriptively, e.g.:
           "hackathon2025 UI: render goodbye page"
           "hackathon2025 UI: render xyz page"
       - In each test:
           - Navigate to the appropriate URL (e.g. http://localhost:8080/goodbye).
           - Assert that the page loads without error.
           - Assert that the page title and main heading (h1) contain meaningful expected text.
           - Assert that key buttons/links or text snippets from the template are visible.
           - If the page triggers REST calls (e.g. via fetch), simulate a click and assert
             that the response is rendered on the page (similar to the index test).

    General rules for the generated TypeScript file:

    - The file name must be: ui-hackathon2025.spec.ts
    - Use:
        import {{ test, expect }} from '@playwright/test';
    - Use Playwright's recommended selectors:
        page.getByRole(...), page.getByText(...), page.locator(...)
    - Use `await page.goto('http://localhost:8080/...')` with the correct paths from the controllers.
    - DO NOT start/stop the backend in the tests; assume it is already running.
    - Keep the first index test name EXACTLY:
        'hackathon2025 UI: initial render and REST interaction'
      and only change selectors/expectations if the provided HTML/controllers clearly require it.
    - For additional tests, choose clear, unique names.

    Output ONLY the TypeScript code for the test file (no explanations, no comments).
    """)


def main():
    # Wir nehmen an: dieses Skript liegt in scripts/, Repo-Root ist eine Ebene höher
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    controllers_dir = repo_root / "src/main/java/com/example/hackathon2025"
    templates_dir = repo_root / "src/main/resources/templates"

    controllers = collect_controllers(controllers_dir)
    templates = collect_templates(templates_dir)

    if not controllers:
        print(f"[WARN] Keine Controller unter {controllers_dir} gefunden.")
    if not templates:
        print(f"[WARN] Keine HTML-Templates unter {templates_dir} gefunden.")

    prompt = build_prompt(controllers, templates)

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
