#!/usr/bin/env python3
"""
generate_ui_tests_with_azure_openai.py

Erzeugt EIN Playwright-Testfile für:

- Die Startseite (GET /, index.html) – UI-Test mit Button und REST-Aufruf
- Alle REST-Endpoints unter /api/... – API-Tests via Playwright request
- Zusätzliche HTML-Seiten, die über Spring MVC Controller gerendert werden
  (z.B. Methoden mit @GetMapping("/foo") und Rückgabewert String "foo").

Strenge Regeln:
- KEINE erfundenen Routen oder Seiten
- Nur Routen testen, die klar aus den Controllern hervorgehen
- Nur Titel testen, wenn im Template ein <title> steht
- Keine fragilen String-Tricks wie .replace(' ', '') zum Vergleichen

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


def collect_templates(templates_dir: pathlib.Path):
    """
    Sammelt alle .html-Templates.
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


def get_index_html(templates) -> str:
    """
    Sucht index.html in der Templates-Liste.
    """
    for t in templates:
        if t["name"].lower().startswith("index."):
            return t["code"]
    return templates[0]["code"] if templates else ""


def build_prompt(controllers, templates) -> str:
    controllers_str = ""
    for c in controllers:
        controllers_str += f"\nController {c['name']} (Pfad: {c['path']}):\n```java\n{c['code']}\n```\n"

    templates_str = ""
    for t in templates:
        templates_str += f"\nTemplate {t['name']} (Pfad: {t['path']}):\n```html\n{t['code']}\n```\n"

    index_html = get_index_html(templates)

    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    There is an index page (GET /) rendered via a Thymeleaf template, one or more
    additional HTML pages, and several REST endpoints implemented in Spring
    controllers (especially under /api/... paths).

    Your job is to generate ONE Playwright test file in TypeScript named
    `ui-hackathon2025.spec.ts` that contains:

    1) A UI test for the index page (GET /)
    2) UI tests for additional HTML pages rendered by Spring MVC controllers
       (non-REST controllers that return view names as String)
    3) API tests for all REST endpoints whose path clearly starts with /api/
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

    === CONTROLLERS AND TEMPLATES (FULL CONTEXT) ===

    Here are all Java controllers:

    {controllers_str}

    Here are all HTML templates:

    {templates_str}

    === TASK 2: ADDITIONAL HTML PAGES (UI TESTS) ===

    From the controllers and templates above, you MUST:

    - Identify Spring MVC controller methods (typically in classes annotated with @Controller)
      that:
        - Use @GetMapping, @RequestMapping, etc.
        - Return a String view name (e.g. "goodby", "followup", "pageX")
        - Are NOT annotated with @ResponseBody and not part of a @RestController class.
    - For each such method:
        - Determine the path (e.g. "/goodby", "/followup") and the view name.
        - Match the view name to a template file with the same or very similar name
          (e.g. goodby.html for "goodby").
        - Create a dedicated UI test in the SAME file (ui-hackathon2025.spec.ts).

    For these additional page tests:

    - Use test names like:
        test('hackathon2025 UI: render goodby page', async ({{ page }}) => {{ ... }})
    - Steps:
        - await page.goto('http://localhost:8080<path>');
        - Assert that the page loads without error.
        - If the template clearly has a <title>, you may assert that the title
          contains a relevant word (e.g. 'Hackathon' or part of the view title).
        - Always assert that there is a main heading:
            const heading = page.getByRole('heading', {{ level: 1 }});
            await expect(heading).toBeVisible();
          and, if the template shows a clear text (e.g. "Goodby Page"), assert
          that heading contains that text (using contains, not exact equality).
        - Assert that clearly visible key texts, buttons, or links exist,
          based on the HTML template (use getByRole/getByText/locator).

    IMPORTANT RULES for these UI page tests:

    - DO NOT invent any routes like "/followup" if there is no corresponding
      controller method and template.
    - Only create tests for controller methods and views that are clearly present
      in the provided controllers and templates.
    - Only assert on <title> if the template clearly contains a <title> element.
      Otherwise, skip title checks for that page.
    - Prefer robust checks (contains, regex) over exact equality.

    === TASK 3: API ENDPOINTS (REST TESTS) ===

    From the controllers, also:

    - Identify all REST endpoints (methods annotated with @GetMapping, @PostMapping,
      @RequestMapping, etc.) whose path clearly starts with '/api/'.
    - For each such endpoint that returns JSON, create a dedicated API test in
      the SAME file (ui-hackathon2025.spec.ts).

    For API tests:

    - Use Playwright's APIRequestContext via the `request` fixture:
        test('...', async ({{ request }}) => {{ ... }})
    - For each /api/... endpoint:
        - Perform a GET (or appropriate method) request to
          'http://localhost:8080<path>'.
        - Assert that the status is 200.
        - Parse the JSON body.
        - Assert that the parsed value is an object and has at least one field.
        - If the controller clearly uses a hard-coded message like
          "Hello from rest api for hackathon 2025!!!", you may:
            - assert that `String(message).toLowerCase()` contains 'hello'.
        - If the controller clearly uses a message like
          "good night from rest api for hackathon 2025!!!", you may:
            - assert that `String(message).toLowerCase()` matches `/good\\s+night/`.
        - DO NOT use tricks like `'good night'.replace(' ', '')` or similar.
        - DO NOT assert on exact full strings unless absolutely necessary.
          Prefer robust checks (contains, regex with optional whitespace).

    GLOBAL RULES:

    - DO NOT invent any endpoints or routes. If there is no controller method for a path,
      IGNORE it completely.
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

    # Alle Templates einsammeln
    templates = []
    for path in templates_dir.rglob("*.html"):
        templates.append(path)

    if not controllers:
        print(f"[WARN] Keine Controller unter {controllers_dir} gefunden.")
    if not templates:
        print(f"[WARN] Keine HTML-Templates unter {templates_dir} gefunden.")

    # Du kannst hier deinen bestehenden Prompt-Aufbau verwenden
    # und z.B. nur Index + APIs dem LLM überlassen.
    prompt = build_prompt(controllers, templates)

    print("[INFO] Rufe Azure OpenAI zur Generierung von Playwright-Tests auf...")
    completion = call_azure_openai_for_playwright(prompt)
    base_ts = strip_code_fences(completion)

    # --- Ab hier: generische UI-Tests für ALLE weiteren HTML-Seiten anhängen ---

    extra_tests = []

    for tpl in templates:
        name = tpl.name  # z.B. "followup.html"
        base = tpl.stem  # z.B. "followup"

        # index.html wird schon im ersten Test abgedeckt
        if base.lower() in ("index", "home", "start"):
            continue

        test_name = f"hackathon2025 UI: render {base} page"
        url_path = f"/{base}"

        extra_ts = f"""
test('{test_name}', async ({'{'} page {'}'}) => {{
  await page.goto('http://localhost:8080{url_path}');
  const heading = page.getByRole('heading', {{ level: 1 }});
  await expect(heading).toBeVisible();
}});
""".strip()

        extra_tests.append(extra_ts)

    full_ts = base_ts.strip() + "\n\n" + "\n\n".join(extra_tests)

    tests_dir = repo_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    target_path = tests_dir / "ui-hackathon2025.spec.ts"
    target_path.write_text(full_ts, encoding="utf-8")

    print(f"[OK] Playwright UI-Test geschrieben (inkl. generischer HTML-Tests): {target_path}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
