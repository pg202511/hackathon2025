#!/usr/bin/env python3
import os
import pathlib
import textwrap
import json
import requests

API_VERSION = "2024-02-15-preview"  # ggf. anpassen

def read_file(path: pathlib.Path) -> str:
    if not path.exists():
        raise SystemExit(f"Datei nicht gefunden: {path}")
    return path.read_text(encoding="utf-8")

def call_azure_openai_for_playwright(controller_code: str, html_code: str) -> str:
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
        "Given a Java Spring Boot controller and an HTML/Thymeleaf template, "
        "you generate high-quality Playwright tests in TypeScript. "
        "The tests should focus on happy-path flows, basic validation, and visible UI elements. "
        "The code must be valid TypeScript for @playwright/test and should be self-contained. "
        "Do NOT explain anything, only output the test file content."
    )

    user_prompt = textwrap.dedent(f"""
    Here is a Spring Boot controller and the corresponding HTML template.
    Generate a Playwright test file `ui-smoke.spec.ts` that:

    - opens `http://localhost:8080/`
    - verifies the page title and main heading
    - verifies that the main button(s) and navigation links are visible
    - tests the 'Hello' UI flow if such an element exists (button/link/text).

    Controller:
    ```java
    {controller_code}
    ```

    Template:
    ```html
    {html_code}
    ```

    Output only valid TypeScript code using:
      import {{ test, expect }} from '@playwright/test';
    """)

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # kein temperature, kein max_tokens → kompatibel mit o3 / neuen Modellen
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=90)
    if resp.status_code >= 400:
        raise RuntimeError(f"Azure OpenAI Fehler {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def strip_code_fences(text: str) -> str:
    import re
    match = re.search(r"```(?:ts|typescript)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def main():
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    web_controller_path = repo_root / "src/main/java/com/example/hackathon2025/WebController.java"
    index_html_path = repo_root / "src/main/resources/templates/index.html"

    controller_code = read_file(web_controller_path)
    html_code = read_file(index_html_path)

    print("[INFO] Rufe Azure OpenAI zur Generierung von Playwright-Tests auf...")
    completion = call_azure_openai_for_playwright(controller_code, html_code)
    ts_code = strip_code_fences(completion)

    tests_dir = repo_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    target_path = tests_dir / "ui-smoke.spec.ts"
    target_path.write_text(ts_code, encoding="utf-8")

    print(f"[OK] Playwright UI-Test geschrieben: {target_path}")

if __name__ == "__main__":
    main()
