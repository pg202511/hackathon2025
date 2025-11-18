#!/usr/bin/env python3
"""
generate_tests_with_azure_openai.py

Erzeugt oder aktualisiert JUnit-5-Tests für geänderte Java-Klassen
mittels Azure OpenAI.

Erwartet Umgebungsvariablen:
- AZURE_OPENAI_ENDPOINT       z.B. https://<resource>.openai.azure.com
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT     Name des Deployments, z.B. gpt-4o oder o3-mini

Optional (für exakte Diffs):
- GIT_BASE_SHA
- GIT_HEAD_SHA
"""

import os
import subprocess
import argparse
import pathlib
import re
import textwrap
import json
from typing import List, Optional, Tuple

import requests

# ggf. an deine Azure OpenAI API-Version anpassen
API_VERSION = "2024-02-15-preview"


# ---------------------------------------------------------
# Hilfsfunktionen für Git und Dateisystem
# ---------------------------------------------------------
def run(cmd: List[str]) -> subprocess.CompletedProcess:
    """Führt ein Kommando aus und gibt das CompletedProcess zurück."""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def get_changed_java_files(source_dir: pathlib.Path) -> List[pathlib.Path]:
    """
    Findet geänderte Java-Dateien im source_dir.

    Strategie:
    - Wenn GIT_BASE_SHA + GIT_HEAD_SHA vorhanden: git diff BASE...HEAD
    - sonst: git diff HEAD~1...HEAD (Fallback)
    - Wenn daraus keine Java-Files resultieren: Fallback auf *alle* Java-Files unter source_dir
    """
    base = os.getenv("GIT_BASE_SHA")
    head = os.getenv("GIT_HEAD_SHA")

    print(f"[INFO] GIT_BASE_SHA={base}, GIT_HEAD_SHA={head}")

    diff_output = ""
    # Versuche gezielten Diff
    try:
        if base and head:
            print(f"[INFO] Verwende Diff: {base}...{head}")
            proc = run(["git", "diff", "--name-only", f"{base}...{head}"])
        else:
            print("[INFO] Verwende Fallback-Diff: HEAD~1...HEAD")
            proc = run(["git", "diff", "--name-only", "HEAD~1...HEAD"])

        if proc.returncode != 0:
            print(f"[WARN] git diff Fehlermeldung:\n{proc.stderr}")
        diff_output = proc.stdout
    except Exception as e:
        print(f"[WARN] Konnte git diff nicht ausführen: {e}")
        diff_output = ""

    changed_files: List[pathlib.Path] = []

    for line in diff_output.splitlines():
        line = line.strip()
        if not line:
            continue
        p = pathlib.Path(line)
        if p.suffix == ".java" and source_dir in p.parents:
            changed_files.append(p)

    if changed_files:
        print("[INFO] Geänderte Java-Dateien (aus git diff):")
        for f in changed_files:
            print(f"  - {f}")
        return changed_files

    # Fallback: Alle Java-Dateien unter source_dir
    print("[INFO] Keine geänderten Java-Dateien via git diff gefunden.")
    print("[INFO] Fallback: verwende ALLE Java-Sourcen unter", source_dir)
    all_java = list(source_dir.rglob("*.java"))
    for f in all_java:
        print(f"  - {f}")
    return all_java


def extract_package_and_class(java_source: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrahiert package-Name und Klassenname aus Java-Quelltext."""
    package_match = re.search(r"package\s+([a-zA-Z0-9_.]+)\s*;", java_source)
    class_match = re.search(r"(public\s+)?class\s+([A-Za-z0-9_]+)", java_source)
    package_name = package_match.group(1) if package_match else None
    class_name = class_match.group(2) if class_match else None
    return package_name, class_name


# ---------- Bootstrap-Erkennung ---------------------------------------------
def is_bootstrap_class(java_source: str, class_name: Optional[str]) -> bool:
    """
    Erkenne typische Bootstrap-Klassen, für die wir KEINE Tests generieren wollen.

    Heuristik:
    - Klasse enthält @SpringBootApplication
    - oder Klassenname endet auf 'Application'
    """
    if not class_name:
        return False

    if "@SpringBootApplication" in java_source:
        return True

    if class_name.endswith("Application"):
        return True

    return False


# ---------------------------------------------------------
# Azure OpenAI Aufruf (ohne max_tokens / temperature)
# ---------------------------------------------------------
def call_azure_openai(prompt: str) -> str:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    # WICHTIG: kein max_tokens, keine temperature → kompatibel mit z.B. o3-mini
    body = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior Java developer and test engineer. "
                    "Generate high-quality, compilable JUnit 5 test classes. "
                    "Focus on meaningful edge cases, null handling, and business rules. "
                    "Do NOT change production code; only produce test code. "
                    "Use JUnit 5 (org.junit.jupiter.api.*) and, if appropriate, Mockito."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"Azure OpenAI Fehler {resp.status_code}: {resp.text}")
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return content


def strip_code_fences(text: str) -> str:
    """
    Entfernt ```java ...``` oder ``` ...``` Codeblöcke, falls vorhanden,
    und gibt nur den reinen Java-Code zurück.
    """
    match = re.search(r"```(?:java)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


# ---------------------------------------------------------
# Generierung der Testdateien
# ---------------------------------------------------------
def generate_test_for_file(source_file: pathlib.Path,
                           source_dir: pathlib.Path,
                           test_dir: pathlib.Path) -> None:
    java_source = source_file.read_text(encoding="utf-8")
    package_name, class_name = extract_package_and_class(java_source)
    if not class_name:
        print(f"[WARN] Keine Klasse in {source_file} erkannt, überspringe.")
        return

    # Bootstrap-Klassen (z. B. Hackathon2025Application) überspringen
    if is_bootstrap_class(java_source, class_name):
        print(f"[INFO] Bootstrap-Klasse erkannt ({class_name}), keine Tests generiert.")
        return

    # Pfad relativ zum source_dir abbilden
    rel = source_file.relative_to(source_dir)
    test_rel = rel.with_name(f"{class_name}Test.java")
    target_path = test_dir / test_rel
    target_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = textwrap.dedent(f"""
    Hier ist eine Java-Klasse aus einem produktiven Service.
    Erzeuge eine passende JUnit-5-Testklasse. Anforderungen:

    - Nutze JUnit 5 (`org.junit.jupiter.api.*`).
    - Erzeuge sinnvolle Testmethoden: Normalfall, Edge Cases, Fehlerfälle.
    - Verwende, wenn sinnvoll, Mockito (`org.mockito.*`) zum Mocking.
    - Stelle sicher, dass der Code kompilierbar ist.
    - Teste explizit die öffentlich sichtbaren Methoden.
    - Nutze die gleiche package-Deklaration wie die Quellklasse.

    Quell-Datei (Pfad): {source_file}
    Quell-Code:
    ---
    {java_source}
    ---
    Gib NUR den Java-Code der Testklasse zurück.
    """)

    print(f"[INFO] Rufe Azure OpenAI für Tests zu {source_file} auf...")
    completion = call_azure_openai(prompt)
    test_code = strip_code_fences(completion)

    # Sicherstellen, dass package-Deklaration vorhanden ist
    if package_name and f"package {package_name}" not in test_code:
        test_code = f"package {package_name};\n\n{test_code}"

    target_path.write_text(test_code, encoding="utf-8")
    print(f"[OK] Test geschrieben: {target_path}")


# ---------------------------------------------------------
# main
# ---------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erzeugt/aktualisiert JUnit-Tests mittels Azure OpenAI für geänderte Java-Dateien."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        help="Pfad zu src/main/java",
    )
    parser.add_argument(
        "--test-dir",
        required=True,
        help="Pfad zu src/test/java",
    )
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source-dir).resolve() if hasattr(args, "source-dir") else pathlib.Path(args.source_dir).resolve()
    test_dir = pathlib.Path(args.test_dir).resolve()

    if not source_dir.exists():
        raise SystemExit(f"Source-Verzeichnis existiert nicht: {source_dir}")

    changed_files = get_changed_java_files(source_dir)

    if not changed_files:
        print("[INFO] Keine Java-Dateien gefunden – nichts zu tun.")
        return

    print("[INFO] Java-Dateien, für die Tests erzeugt werden:")
    for f in changed_files:
        print(f"  - {f}")

    for f in changed_files:
        try:
            generate_test_for_file(f, source_dir, test_dir)
        except Exception as e:
            print(f"[ERROR] Fehler beim Generieren von Tests für {f}: {e}")


if __name__ == "__main__":
    main()
