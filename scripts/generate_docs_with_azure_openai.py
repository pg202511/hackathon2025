#!/usr/bin/env python3
"""
generate_docs_with_azure_openai.py

Erzeugt eine technische und architektonische Dokumentation für das Projekt
als Markdown-Datei (docs/architecture.md) mittels Azure OpenAI.

Inhaltlich soll die Dokumentation u.a. abdecken:
- Überblick (Zweck der Anwendung)
- Architektur (Backend, UI, REST-APIs)
- Wichtige Klassen (Controller, Application)
- Wichtige Endpunkte (/api/...)
- UI-Struktur (Thymeleaf-Templates)
- Teststrategie (JUnit, Playwright, AI-generierte Tests)
- CI/CD-Workflows (GitHub Actions + Azure OpenAI)

Erwartet Umgebungsvariablen:
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT
"""

import os
import pathlib
import textwrap
import json
import re
import requests
from typing import List, Dict

API_VERSION = "2024-02-15-preview"  # ggf. anpassen


def read_file(path: pathlib.Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def collect_java_files(base_dir: pathlib.Path) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    if not base_dir.exists():
        return result
    for path in base_dir.rglob("*.java"):
        code = read_file(path)
        if not code.strip():
            continue
        result.append(
            {
                "name": path.name,
                "path": str(path.relative_to(base_dir.parent)),
                "code": code,
            }
        )
    return result


def collect_templates(templates_dir: pathlib.Path) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    if not templates_dir.exists():
        return result
    for path in templates_dir.rglob("*.html"):
        code = read_file(path)
        if not code.strip():
            continue
        result.append(
            {
                "name": path.name,
                "path": str(path.relative_to(templates_dir.parent)),
                "code": code,
            }
        )
    return result


def call_azure_openai(prompt: str) -> str:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    system_prompt = (
        "You are a senior software architect. "
        "You create concise but clear technical and architectural documentation "
        "for Java/Spring Boot web applications with REST APIs and simple UIs. "
        "You write in Markdown, with headings, bullet lists, and code blocks where useful. "
        "You do NOT invent features that are not visible in the code. "
        "If something is unclear, you describe it carefully as an assumption."
    )

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        # kein max_tokens / keine temperature -> Azure-kompatibel
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=120)
    if resp.status_code >= 400:
        raise RuntimeError(f"Azure OpenAI Fehler {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def strip_markdown_fences(text: str) -> str:
    # Falls das Modell ```markdown ...``` drum herum legt
    match = re.search(r"```(?:markdown)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def build_prompt(java_files, templates) -> str:
    # Begrenze Kontext etwas, um nicht alles 1:1 reinzuschütten
    # (für Hackathongröße reicht das grob)
    def shorten(code: str, max_lines: int = 200) -> str:
        lines = code.splitlines()
        if len(lines) <= max_lines:
            return code
        return "\n".join(lines[:max_lines]) + "\n// ... truncated ..."

    java_snippets = []
    for jf in java_files:
        java_snippets.append(
            f"Datei: {jf['path']}\n```java\n{shorten(jf['code'])}\n```"
        )

    template_snippets = []
    for t in templates:
        template_snippets.append(
            f"Template: {t['path']}\n```html\n{shorten(t['code'], max_lines=120)}\n```"
        )

    java_block = "\n\n".join(java_snippets)
    tmpl_block = "\n\n".join(template_snippets)

    return textwrap.dedent(f"""
    Please create a technical and architectural documentation in **Markdown** for the
    following Java/Spring Boot demo project "hackathon2025".

    The documentation will live in the repository as `docs/architecture.md` and should be
    understandable for other developers joining the project.

    ### Style & Tone

    - Write in English.
    - Use Markdown headings (##, ###, etc).
    - Be concise but clear.
    - Prefer bullet lists for enumerations.
    - Include small code blocks where it helps (but do not paste full files).
    - Add a short note at the top that this document is AI-assisted and should be reviewed.

    ### Mandatory Sections

    Please include at least the following sections:

    1. Introduction
       - What the application does (based purely on the code and HTML templates).
       - Main technologies (Spring Boot, Java, Thymeleaf, REST APIs, etc.).

    2. Architecture Overview
       - High-level architecture (Backend, Controllers, REST APIs, UI templates).
       - How the main application class wires things together.
       - Request flow: Browser -> Controller -> View / REST endpoint.

    3. Domain & Components
       - Important controllers and their responsibilities.
       - Overview of REST endpoints (/api/...) and what they return.
       - Overview of HTML pages (index, followup, etc.) and their purpose.

    4. UI & REST Interaction
       - Describe the index page behavior (button "Test REST", /api/hello JSON response).
       - Describe other relevant pages (e.g. followup) based on their HTML content.

    5. Testing Strategy
       - Unit tests with JUnit (generated via Azure OpenAI).
       - UI/API tests with Playwright (generated via Azure OpenAI).
       - How the tests roughly validate the application (no need to list every assertion).

    6. CI/CD & AI-Assisted Workflows
       - Describe that GitHub Actions workflows:
         - generate/update unit tests for Java using Azure OpenAI,
         - generate/update Playwright UI/API tests using Azure OpenAI,
         - run Maven tests and Playwright tests in CI,
         - (optionally) auto-commit generated tests to the PR branch.
       - Mention that this document itself is generated by an AI workflow and should be
         reviewed and refined by humans.

    7. Limitations & Next Steps
       - Point out obvious limitations of the current architecture (e.g. simple demo nature).
       - Suggest next steps (more layers, services, configuration, error handling, etc.).

    ### Source Code Context

    Here are the most relevant Java files:

    {java_block}

    Here are the HTML templates:

    {tmpl_block}

    Please now produce the full Markdown content for `docs/architecture.md`.
    """)


def main() -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    java_src_dir = repo_root / "src/main/java/com/example/hackathon2025"
    templates_dir = repo_root / "src/main/resources/templates"

    java_files = collect_java_files(java_src_dir)
    templates = collect_templates(templates_dir)

    if not java_files:
        print(f"[WARN] Keine Java-Dateien unter {java_src_dir} gefunden.")
    if not templates:
        print(f"[WARN] Keine HTML-Templates unter {templates_dir} gefunden.")

    prompt = build_prompt(java_files, templates)

    print("[INFO] Rufe Azure OpenAI zur Generierung der Architektur-Dokumentation auf...")
    completion = call_azure_openai(prompt)
    md = strip_markdown_fences(completion)

    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    target_path = docs_dir / "architecture.md"

    header = (
        "<!--\n"
        "  This document was initially generated with the help of Azure OpenAI.\n"
        "  Please review and adapt it as needed.\n"
        "-->\n\n"
    )

    target_path.write_text(header + md + "\n", encoding="utf-8")
    print(f"[OK] Architektur-Dokumentation geschrieben: {target_path}")


if __name__ == "__main__":
    main()
