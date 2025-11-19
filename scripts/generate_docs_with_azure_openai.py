#!/usr/bin/env python3
"""
generate_docs_with_azure_openai.py

Erzeugt eine technische und architektonische Dokumentation für das Projekt
als Markdown-Datei (docs/architecture.md).

Strategie:
- Versucht zuerst, eine Doku via Azure OpenAI zu erzeugen.
- Falls die Antwort offensichtlich unbrauchbar ist (z.B. nur ein Java-Snippet,
  sehr kurz, keine Markdown-Überschriften), wird automatisch auf einen
  deterministischen Fallback-Generator zurückgegriffen, der aus dem Code
  eine Markdown-Doku zusammenbaut.

Erwartet (für den Azure-Teil) Umgebungsvariablen:
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


# ---------- Hilfsfunktionen: Dateien einlesen ----------

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


# ---------- Azure OpenAI Aufruf ----------

def call_azure_openai(prompt: str) -> str:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")

    if not endpoint or not api_key or not deployment:
        raise RuntimeError("Azure OpenAI Umgebungsvariablen sind nicht gesetzt.")

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


# ---------- Qualitätscheck für die AI-Antwort ----------

def looks_like_bad_doc(md: str) -> bool:
    """
    Heuristik: ist die generierte Doku offensichtlich Müll?
    - sehr kurz
    - keine Markdown-Überschriften
    - sieht eher wie nackter Java-Code aus
    """
    s = md.strip()

    if len(s) < 300:
        return True

    if "# " not in s and "## " not in s:
        return True

    # Wenn das Ding mit "java" anfängt und keine Überschriften enthält → verdächtig
    first_line = s.splitlines()[0].strip().lower()
    if first_line.startswith("java") and "## " not in s and "# " not in s:
        return True

    # Wenn @SpringBootApplication drin ist, aber keine echten Doku-Abschnitte
    if "@SpringBootApplication" in s and "## Introduction" not in s and "# Introduction" not in s:
        return True

    return False


# ---------- Prompt für Azure ----------

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
    2. Architecture Overview
    3. Components and Responsibilities
    4. UI and REST Interaction
    5. Testing Strategy
    6. CI/CD and AI-Assisted Workflows
    7. Limitations and Next Steps

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


# ---------- Fallback-Doku ohne Azure ----------

def extract_package_name(java_code: str) -> str:
    m = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+)\s*;", java_code, re.MULTILINE)
    return m.group(1) if m else ""


def extract_class_name(code: str, fallback: str) -> str:
    m = re.search(r"class\s+([A-Za-z0-9_]+)", code)
    if m:
        return m.group(1)
    return fallback


def extract_endpoints(java_code: str) -> List[Dict[str, str]]:
    endpoints = []

    def add_matches(http_method: str, pattern: str):
        for m in re.finditer(pattern, java_code):
            path = m.group(1)
            endpoints.append({"method": http_method, "path": path})

    # Simple Heuristik für @GetMapping, @PostMapping, @RequestMapping
    add_matches("GET", r"@GetMapping\(\s*\"([^\"]+)\"\s*\)")
    add_matches("POST", r"@PostMapping\(\s*\"([^\"]+)\"\s*\)")
    add_matches("REQUEST", r"@RequestMapping\(\s*\"([^\"]+)\"\s*\)")

    return endpoints


def extract_h1_from_template(html: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    # HTML-Tags entfernen
    inner = re.sub(r"<[^>]+>", "", m.group(1))
    return inner.strip()


def build_fallback_doc(java_files, templates) -> str:
    # Controller & Endpoints sammeln
    controllers = []
    for jf in java_files:
        code = jf["code"]
        if "@RestController" in code or "@Controller" in code:
            pkg = extract_package_name(code)
            cls = extract_class_name(code, jf["name"].replace(".java", ""))
            endpoints = extract_endpoints(code)
            controllers.append(
                {
                    "package": pkg,
                    "class": cls,
                    "path": jf["path"],
                    "endpoints": endpoints,
                    "rest": "@RestController" in code,
                }
            )

    # Templates sammeln
    template_infos = []
    for t in templates:
        h1 = extract_h1_from_template(t["code"])
        template_infos.append(
            {
                "name": t["name"],
                "path": t["path"],
                "h1": h1,
            }
        )

    # Markdown aufbauen
    lines: List[str] = []

    lines.append("# Hackathon2025 – Technical and Architectural Documentation\n")
    lines.append(
        "This document was generated automatically based on the current source code and HTML templates. "
        "It provides a high-level overview of the architecture, components, endpoints and UI structure "
        "of the `hackathon2025` Spring Boot demo application.\n"
    )

    # Introduction
    lines.append("## Introduction\n")
    lines.append(
        "The `hackathon2025` project is a small Spring Boot web application used to demonstrate "
        "AI-assisted development workflows. It combines:\n"
    )
    lines.append("- A Java 17 / Spring Boot backend\n")
    lines.append("- REST endpoints implemented in annotated controllers (e.g. `/api/hello`)\n")
    lines.append("- Simple HTML/Thymeleaf-based views (e.g. `index.html`, additional pages)\n")
    lines.append("- Automatically generated unit tests (JUnit) and UI/API tests (Playwright)\n")
    lines.append(
        "- CI pipelines that call Azure OpenAI to generate tests and documentation inside GitHub Actions\n"
    )

    # Architecture Overview
    lines.append("\n## Architecture Overview\n")
    lines.append(
        "The application follows a typical Spring Boot architecture:\n\n"
        "- **Bootstrap / Application class** – starts the Spring context and embedded Tomcat.\n"
        "- **Controllers** – handle HTTP requests and either render views or return JSON responses.\n"
        "- **Templates** – HTML files under `src/main/resources/templates` that define the UI.\n"
        "- **REST APIs** – JSON endpoints under `/api/...` for programmatic access.\n"
    )

    # Components & Controllers
    lines.append("\n## Components and Responsibilities\n")

    if controllers:
        lines.append("### Controllers\n")
        lines.append(
            "The following controllers were detected based on `@Controller` / `@RestController` annotations:\n"
        )
        for c in controllers:
            lines.append(f"- `{c['class']}`  \n"
                         f"  - Package: `{c['package'] or '(default)'}`  \n"
                         f"  - Source: `{c['path']}`  \n"
                         f"  - Type: {'REST controller' if c['rest'] else 'MVC controller'}")
            if c["endpoints"]:
                lines.append("  - Endpoints:")
                for ep in c["endpoints"]:
                    lines.append(
                        f"    - `{ep['method']}` `{ep['path']}`"
                    )
            else:
                lines.append("  - Endpoints: (no @GetMapping/@PostMapping/@RequestMapping with string literal found)")
        lines.append("")
    else:
        lines.append(
            "No controllers with `@Controller` or `@RestController` annotations were found in the scanned sources.\n"
        )

    # Templates
    lines.append("### HTML Templates\n")
    if template_infos:
        lines.append(
            "The following HTML templates were found under `src/main/resources/templates`:\n"
        )
        for t in template_infos:
            desc = f"`{t['name']}` (path: `{t['path']}`"
            if t["h1"]:
                desc += f", main heading: \"{t['h1']}\""
            desc += ")"
            lines.append(f"- {desc}")
        lines.append("")
    else:
        lines.append("No HTML templates were found.\n")

    # UI & REST Interaction
    lines.append("## UI and REST Interaction\n")
    lines.append(
        "The main entry page (`index.html`) is typically served at `GET /` by an MVC controller. "
        "It renders a heading, some descriptive text, and UI elements such as buttons.\n\n"
        "Based on the existing code and templates, the core interaction pattern is:\n"
    )
    lines.append(
        "1. The browser requests a view (e.g. `/`).\n"
        "2. A Spring MVC controller returns a view name (e.g. `index`), which is rendered by a Thymeleaf template.\n"
        "3. JavaScript on the page can call REST endpoints (e.g. `/api/hello`) via `fetch`.\n"
        "4. The JSON response from the REST controller is displayed in the UI (e.g. in a `<p id=\"apiResult\">`).\n"
    )

    # Testing Strategy
    lines.append("\n## Testing Strategy\n")
    lines.append(
        "The project is designed to showcase AI-assisted test generation. The typical setup is:\n\n"
        "- **JUnit 5 unit tests** under `src/test/java` for controllers and other classes.\n"
        "- Tests are generated or updated by a script `scripts/generate_tests_with_azure_openai.py`,\n"
        "  which calls Azure OpenAI to propose test cases.\n"
        "- **Playwright UI/API tests** in `tests/ui-hackathon2025.spec.ts`, generated by\n"
        "  `scripts/generate_ui_tests_with_azure_openai.py`.\n"
        "- Playwright tests cover:\n"
        "  - Rendering of the index page.\n"
        "  - Clicking the \"Test REST\" button and verifying the `/api/hello` JSON response.\n"
        "  - Direct HTTP calls to `/api/...` endpoints via Playwright's `request` fixture.\n"
    )

    # CI/CD & AI
    lines.append("\n## CI/CD and AI-Assisted Workflows\n")
    lines.append(
        "GitHub Actions workflows orchestrate the build, test and documentation pipelines. "
        "Typical workflows include:\n\n"
        "- **Java CI with Azure OpenAI test generation** – runs on pull requests to `main`:\n"
        "  - checks out the PR branch,\n"
        "  - runs `generate_tests_with_azure_openai.py` to create/update unit tests,\n"
        "  - executes `mvn clean verify`,\n"
        "  - and, if all tests pass, commits the updated tests back into the PR branch.\n\n"
        "- **Playwright UI/API tests with Azure OpenAI** – builds and starts the Spring Boot app, then:\n"
        "  - runs `generate_ui_tests_with_azure_openai.py` to update the Playwright tests,\n"
        "  - executes `npx playwright test`,\n"
        "  - and commits updated tests when the run is green.\n\n"
        "- **Architecture docs generation** – runs `generate_docs_with_azure_openai.py` to generate\n"
        "  or update this `docs/architecture.md` file and commit it into the PR branch.\n\n"
        "All AI-generated artifacts (tests, docs) are treated as proposals in a pull request and are "
        "only merged into `main` after human review.\n"
    )

    # Limitations & Next Steps
    lines.append("\n## Limitations and Next Steps\n")
    lines.append(
        "The current architecture is intentionally simple and optimized for demonstration purposes. "
        "Some typical limitations and potential improvements are:\n"
    )
    lines.append(
        "- No persistence layer (database) – all responses are in-memory / hard-coded.\n"
    )
    lines.append(
        "- Limited error handling and validation – real-world applications would need more robust handling "
        "of invalid requests, exceptions and security concerns.\n"
    )
    lines.append(
        "- Controllers mix simple demo logic and HTTP handling; larger systems often introduce service "
        "layers and DTOs for better separation of concerns.\n"
    )
    lines.append(
        "- AI-generated tests and documentation provide a good starting point but should always be "
        "reviewed, refined and extended by humans.\n"
    )
    lines.append(
        "- Future work could include: adding persistence, more complex domain logic, integration tests, "
        "API documentation (e.g. via OpenAPI/Swagger) and more detailed architecture diagrams.\n"
    )

    return "\n".join(lines)


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

    # 1) Versuchen, Azure OpenAI zu verwenden
    md = ""
    used_fallback = False
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        try:
            prompt = build_prompt(java_files, templates)
            print("[INFO] Rufe Azure OpenAI zur Generierung der Architektur-Dokumentation auf ...")
            completion = call_azure_openai(prompt)
            md_candidate = strip_markdown_fences(completion)
            if looks_like_bad_doc(md_candidate):
                print("[WARN] Azure OpenAI Antwort sieht nach unvollständiger Doku aus – Fallback wird verwendet.")
                used_fallback = True
            else:
                md = md_candidate
        except Exception as e:
            print(f"[WARN] Azure OpenAI konnte nicht verwendet werden: {e}")
            used_fallback = True
    else:
        print("[WARN] Azure OpenAI ist nicht konfiguriert – Fallback wird verwendet.")
        used_fallback = True

    # 2) Fallback, falls nötig
    if used_fallback:
        md = build_fallback_doc(java_files, templates)

    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    target_path = docs_dir / "architecture.md"

    header = (
        "<!--\n"
        "  This document was initially generated automatically (Azure OpenAI and/or static analysis).\n"
        "  Please review and adapt it as needed.\n"
        "-->\n\n"
    )

    target_path.write_text(header + md + "\n", encoding="utf-8")
    print(f"[OK] Architektur-Dokumentation geschrieben: {target_path}")


if __name__ == "__main__":
    main()
