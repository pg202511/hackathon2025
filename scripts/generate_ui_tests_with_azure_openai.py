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
    # Hier beschreiben wir dein aktuelles UI-Verhalten EXAKT
    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    The main HTML (index.html) looks like this (simplified):

    ```html
    {index_html}
    ```

    Important behavior:

    - On initial load:
      - The page is served at GET /.
      - The <title> contains something like "Hackathon".
      - The main <h1> heading contains "Hackathon 2025 Demo".
      - There is a button with text "Test REST" that calls the JavaScript function callApi().
      - There is a <p id="apiResult"></p> element.
      - Initially, the #apiResult paragraph is present in the DOM but empty. It may effectively be hidden
        (zero height), so DO NOT assert that it is visible. Only assert that it is attached and its
        text content is an empty string.

    - On user interaction:
      - When the user clicks the "Test REST" button, the function callApi() does:
          fetch('/api/hello')
          then reads the JSON
          then sets document.getElementById('apiResult').innerText = JSON.stringify(json)
      - After the click, #apiResult should have a non-empty text content that is valid JSON.
        You can parse it with JSON.parse and assert that the resulting object has at least one field,
        and that it likely contains some kind of "hello" message. Do NOT rely on an exact JSON shape,
        but you can check that the raw text contains 'Hello' (case-insensitive).

    Your task:

    Generate a single Playwright test file in TypeScript, named `ui-hackathon2025.spec.ts`, that:

    1. Opens `http://localhost:8080/`.
    2. Verifies:
       - The page title contains 'Hackathon'.
       - The main heading (h1) contains 'Hackathon 2025 Demo'.
       - The button with text 'Test REST' is visible.
       - The #apiResult element is attached to the DOM and its text content is initially an empty string.
         Do NOT assert that it is visible.

    3. Then clicks the 'Test REST' button and verifies:
       - #apiResult eventually has a non-empty text.
       - The text is valid JSON (JSON.parse does not throw).
       - Optionally, the text contains 'Hello' (case-insensitive).

    General rules:
    - Use TypeScript and import from '@playwright/test':
        import {{ test, expect }} from '@playwright/test';
    - Use Playwright test fixtures with `test(...)`.
    - Use robust selectors: `getByRole`, `getByText`, and `locator('#apiResult')`.
    - Assume the base URL is `http://localhost:8080`.
    - Do NOT include any explanations or comments, only the code.

    For context, here are the controllers (optional background information):

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
