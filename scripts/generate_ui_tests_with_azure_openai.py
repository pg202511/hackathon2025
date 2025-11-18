#!/usr/bin/env python3
"""
generate_ui_tests_with_azure_openai.py

Für das Projekt "hackathon2025":

- Liest WebController.java und HelloRestController.java
- Liest index.html
- Ruft Azure OpenAI auf, um einen Playwright-UI-Test zu generieren
- Schreibt: tests/ui-hackathon2025.spec.ts

Erwartet Umgebungsvariablen:
- AZURE_OPENAI_ENDPOINT       z.B. https://<resource>.openai.azure.com
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT     Name des Deployments, z.B. gpt-4o oder o3-mini
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
        # kein temperature, kein max_tokens → kompatibel z.B. mit o3 / neueren Modellen
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


def build_prompt(web_controller: str, hello_controller: str, index_html: str) -> str:
    # Wir beschreiben EXPLIZIT das gewünschte Testmuster
    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    The main HTML (index.html) currently looks like this:

    ```html
    {index_html}
    ```

    The intended UI behavior is:

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

    You must generate a SINGLE Playwright test file in TypeScript named `ui-hackathon2025.spec.ts`.
    The file must:

    - Import Playwright test functions:
        import {{ test, expect }} from '@playwright/test';
    - Contain exactly ONE test named:
        "hackathon2025 UI: initial render and REST interaction"
      (do not change this test name unless the user interface changes in a way that makes this name misleading).

    The test implementation MUST follow this structure:

    1. Navigate to `http://localhost:8080/`.
    2. Assert that the page title contains "Hackathon".
    3. Get the main heading (h1) using getByRole('heading', {{ level: 1 }}) and assert that it contains "Hackathon 2025 Demo".
    4. Get the "Test REST" button using getByRole('button', {{ name: 'Test REST' }}) and assert that it is visible.
    5. Get the locator for '#apiResult':
         const apiResult = page.locator('#apiResult');
       - Assert that count() is > 0 (the element exists):
           const count = await apiResult.count();
           expect(count).toBeGreaterThan(0);
       - Assert that its text content is initially the empty string:
           await expect(apiResult).toHaveText('');
    6. Click the "Test REST" button.
    7. Wait until #apiResult has a non-empty text:
         await expect(apiResult).not.toHaveText('', {{ timeout: 5000 }});
    8. Read the innerText of #apiResult, parse it as JSON, and assert:
       - parsing does not return null,
       - the parsed value is an object,
       - Object.keys(parsed).length > 0,
       - the raw text (toLowerCase()) contains "hello".

    You can adapt SELECTORS or EXPECTED TEXTS ONLY if the provided HTML template or controllers clearly require it
    (for example, the heading text or button label has changed).
    Otherwise, keep the overall structure, test name, and expectations exactly as described.

    Use exactly this pattern in TypeScript:

    ```ts
    import {{ test, expect }} from '@playwright/test';

    test('hackathon2025 UI: initial render and REST interaction', async ({{ page }}) => {{
      // implement the steps described above here
    }});
    ```

    Do NOT output any explanation or comments, only the TypeScript test code.

    For additional context only (do not overfit on these, just use them if helpful),
    here are the controllers:

    WebController:
    ```java
    {web_controller}
    ```

    HelloRestController:
    ```java
    {hello_controller}
    ```
    """)



def main():
    # Skript liegt in scripts/, Repo-Root ist eine Ebene höher
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    controllers_dir = repo_root / "src/main/java/com/example/hackathon2025"
    templates_dir = repo_root / "src/main/resources/templates"

    web_controller_path = controllers_dir / "WebController.java"
    hello_controller_path = controllers_dir / "HelloRestController.java"
    index_html_path = templates_dir / "index.html"

    web_controller = read_file(web_controller_path)
    hello_controller = read_file(hello_controller_path)
    index_html = read_file(index_html_path)

    if not index_html.strip():
        print(f"[WARN] index.html leer oder nicht gefunden: {index_html_path}")

    prompt = build_prompt(web_controller, hello_controller, index_html)

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
