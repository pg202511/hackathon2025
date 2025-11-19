#!/usr/bin/env python3
"""
generate_docs_with_azure_openai.py

Erzeugt eine technische und architektonische Dokumentation für das Projekt
als Markdown-Datei (docs/architecture.md) mittels Azure OpenAI.

Inhaltlich soll die Dokumentation u.a. abdecken:
- Überblick (Zweck der Anwendung)
- Architektur (Backend, UI, REST-APIs)
- Wichtige Klassen (Controller, Application)
- Wichtige Endpunkte (/api/…)
- Wichtige HTML-Templates (index.html, followup.html, …)
- Teststrategie (JUnit, Playwright, AI-generierte Tests)
- CI/CD-Workflows (GitHub Actions + Azure OpenAI)
- Limitierungen & mögliche nächste Schritte

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
from typing import List, Dict

import requests

API_VERSION = "2024-02-15-preview"  # ggf. anpassen


# ---------- Hilfsfunktionen ----------

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
        "You create clear, structured, multi-section technical and architectural documentation "
        "for Java/Spring Boot web applications with REST APIs and HTML/Thymeleaf UIs. "
        "You always write a complete Markdown document with headings and narrative text, "
        "not just a short code snippet. "
        "You do NOT invent features that are not visible in the code. "
        "If something is unclear, you clearly mark it as an assumption."
    )

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        # keine max_tokens / temperature -> Azure-kompatibel
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=180)
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


def shorten_code(code: str, max_lines: int = 200) -> str:
    lines = code.splitlines()
    if len(lines) <= max_lines:
        return code
    return "\n".join(lines[:max_lines]) + "\n// ... truncated ..."


def build_prompt(java_files, templates) -> str:
    java_snippets = []
    for jf in java_files:
        java_snippets.append(
            f"File: {jf['path']}\n```java\n{shorten_code(jf['code'])}\n```"
        )

    template_snippets = []
    for t in templates:
        template_snippets.append(
            f"Template: {t['path']}\n```html\n{shorten_code(t['code'], max_lines=120)}\n```"
        )

    java_block = "\n\n".join(java_snippets)
    tmpl_block = "\n\n".join(template_snippets)

    return textwrap.dedent(f"""
    Please create a **comprehensive technical and architectural documentation** in **Markdown**
    for the following Java/Spring Boot demo project called `hackathon2025`.

    The documentation will be stored as `docs/architecture.md` in the repository and should
    be understandable for new developers joining the project.

    ### Very important output requirements

    - Output **one complete Markdown document**.
    - Do **not** just output a short code snippet.
    - Do **not** simply repeat the full source code.
    - Use headings (`#`, `##`, `###`) and paragraphs.
    - Use bullet lists where appropriate.
    - Include **short** code examples only where they help explain something.
    - Aim for roughly **800–1500 words** (not a one-liner).

    ### Mandatory Sections

    Please include at least the following sections (as Markdown headings):

    1. Introduction
       - What the application does (based purely on the code and HTML templates).
       - Main technologies (Spring Boot, Java, Thymeleaf, REST APIs, Playwright, etc.).

    2. Architecture Overview
       - High-level architecture (backend, controllers, REST APIs, UI templates).
       - How the main application class wires things together.
       - Request flow: Browser → Controller → View / REST endpoint.

    3. Components and Responsibilities
       - Important controllers and their roles (e.g. Hello/Godbye controllers, WebController).
       - Overview of REST endpoints (`/api/...`) and what they return.
       - Overview of HTML pages (e.g. `index.html`, `followup.html`, etc.) and their purpose.

    4. UI and REST Interaction
       - Describe the index page behavior (button "Test REST", `/api/hello` JSON response).
       - Describe other relevant pages based on their HTML content (e.g. followup view if present).
       - Explain how the UI interacts with the REST controllers.

    5. Testing Strategy
       - Unit tests with JUnit (including that some tests are generated with Azure OpenAI).
       - UI/API tests with Playwright (also generated with Azure OpenAI).
       - Explain roughly what is covered (no need to list every single assertion).

    6. CI/CD and AI-Assisted Workflows
       - Explain that GitHub Actions workflows:
         - generate/update unit tests for Java using Azure OpenAI,
         - generate/update Playwright UI/API tests using Azure OpenAI,
         - generate/update this architecture document,
         - run Maven tests and Playwright tests in CI,
         - commit generated artifacts back to the **pull request branch** (not directly to `main`).
       - Mention explicitly that this document itself is generated by an AI workflow
         and should be reviewed and refined by humans.

    7. Limitations and Next Steps
       - Point out obvious limitations of the current architecture (simple demo, no persistence, etc.).
       - Suggest sensible next steps (more layers, validation, error handling, configuration, etc.).

    ### Source Code Context

    Below you find the relevant Java files and HTML templates.
    Use them as the **factual basis** for your documentation.
    Do not paste them back 1:1; summarize and explain them instead.

    #### Java files

    {java_block}

    #### HTML templates

    {tmpl_block}

    Now produce the full Markdown content for `docs/architecture.md`.
    Do NOT wrap the whole document in a single code block.
    """)


# ---------- main ----------

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

    print("[INFO] Rufe Azure OpenAI zur Generierung der Architektur-Dokumentation auf ...")
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
