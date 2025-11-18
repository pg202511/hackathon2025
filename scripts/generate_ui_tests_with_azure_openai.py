#!/usr/bin/env python3
"""
generate_ui_tests_with_azure_openai.py

Spezielle Version für das Projekt "hackathon2025":

- Liest WebController.java und HelloRestController.java
- Liest index.html (und optional hello*.html)
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

API_VERSION = "2024-02-15-preview"  # ggf. an deine Azure OpenAI Ressource anpassen


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
        # kein temperature, kein max_tokens → kompatibel mit neueren Azure-Modellen
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


def build_prompt(web_controller: str, hello_controller: str, index_html: str, extra_templates: dict[str, str]) -> str:
    extras_str = ""
    for name, content in extra_templates.items():
        if not content.strip():
            continue
        extras_str += f"\nTemplate {name}:\n```html\n{content}\n```\n"

    return textwrap.dedent(f"""
    We are working on a Spring Boot demo app called "hackathon2025".
    It runs on http://localhost:8080.

    We have:
    - a WebController that serves the main HTML UI
    - a HelloRestController that exposes a "hello" REST endpoint
    - HTML templates (Thymeleaf or classic HTML) for the UI

    Your task:
    Generate a single Playwright test file `ui-hackathon2025.spec.ts` that:

    1. Opens `http://localhost:8080/`
       - Verifies the page title (e.g. contains "Hackathon" or similar)
       - Verifies the main heading is visible
       - Verifies that key buttons/links are visible (e.g. upload, hello, navigation)

    2. If the UI exposes a way to trigger the hello endpoint via a button or link:
       - Click that element
       - Assert that the expected hello text appears

    3. If there is a form or input field visible on the start page:
       - Fill it with some example value
       - Submit it
       - Check that a response/result appears (e.g. some text or table)

    General rules:
    - Use TypeScript and import from '@playwright/test':
        import {{ test, expect }} from '@playwright/test';
    - Use Playwright test fixtures with `test(...)`.
    - Use robust selectors: `getByRole`, `getByText`, `getByLabel`, etc.
    - Assume the base URL is `http://localhost:8080`.
    - Do NOT include any explanations or comments, only the code.

    Here is the WebController:

    ```java
    {web_controller}
    ```

    Here is the HelloRestController:

    ```java
    {hello_controller}
    ```

    Here is the index.html template:

    ```html
    {index_html}
    ```

    {extras_str}
    """)


def main():
    # Wir nehmen an: dieses Skript liegt in scripts/, Repo-Root ist eine Ebene höher
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    controllers_dir = repo_root / "src/main/java/com/example/hackathon2025"
    templates_dir = repo_root / "src/main/resources/templates"

    web_controller_path = controllers_dir / "WebController.java"
    hello_controller_path = controllers_dir / "HelloRestController.java"
    index_html_path = templates_dir / "index.html"

    web_controller = read_file(web_controller_path)
    hello_controller = read_file(hello_controller_path)
    index_html = read_file(index_html_path)

    extra_templates: dict[str, str] = {}
    # Beispiel: wenn du weitere Templates nutzen möchtest
    for candidate in ["hello.html", "hello.html", "start.html"]:
        p = templates_dir / candidate
        if p.exists():
            extra_templates[p.name] = read_file(p)

    if not web_controller.strip():
        print(f"[WARN] WebController.java leer oder nicht gefunden: {web_controller_path}")
    if not index_html.strip():
        print(f"[WARN] index.html leer oder nicht gefunden: {index_html_path}")

    prompt = build_prompt(web_controller, hello_controller, index_html, extra_templates)

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
