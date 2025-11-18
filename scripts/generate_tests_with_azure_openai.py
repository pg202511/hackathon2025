#!/usr/bin/env python3
import os
import subprocess
import argparse
import pathlib
import re
import textwrap
import json

import requests

API_VERSION = "2024-02-15-preview"  # ggf. anpassen

def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def get_changed_java_files(source_dir: pathlib.Path) -> list[pathlib.Path]:
    """
    Findet geänderte Java-Dateien im source_dir (verglichen mit origin/main).
    """
    try:
        diff_output = run(["git", "diff", "--name-only", "origin/main...HEAD"])
    except RuntimeError:
        # Fallback: alle Files, wenn origin/main im CI nicht vorhanden ist
        diff_output = run(["git", "diff", "--name-only"])

    changed_files = []
    for line in diff_output.splitlines():
        p = pathlib.Path(line)
        if p.suffix == ".java" and source_dir in p.parents:
            changed_files.append(p)
    return changed_files


def extract_package_and_class(java_source: str) -> tuple[str | None, str | None]:
    package_match = re.search(r"package\s+([a-zA-Z0-9_.]+)\s*;", java_source)
    class_match = re.search(r"(public\s+)?class\s+([A-Za-z0-9_]+)", java_source)
    package_name = package_match.group(1) if package_match else None
    class_name = class_match.group(2) if class_match else None
    return package_name, class_name


def call_azure_openai(prompt: str) -> str:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    body = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior Java developer and test engineer. "
                    "Generate high-quality JUnit 5 test classes. "
                    "Focus on meaningful edge cases, null handling, and business rules. "
                    "Do NOT change production code; only produce test code."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "max_tokens": 1200,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return content


def strip_code_fences(text: str) -> str:
    # Entfernt ```java ... ``` Hüllen
    match = re.search(r"```(?:java)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_test_for_file(source_file: pathlib.Path, source_dir: pathlib.Path, test_dir: pathlib.Path):
    java_source = source_file.read_text(encoding="utf-8")
    package_name, class_name = extract_package_and_class(java_source)
    if not class_name:
        print(f"[WARN] Keine Klasse in {source_file} erkannt, überspringe.")
        return

    rel = source_file.relative_to(source_dir)
    # gleicher Paketpfad, aber Dateiname mit 'Test'
    test_rel = rel.with_name(f"{class_name}Test.java")
    target_path = test_dir / test_rel
    target_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = textwrap.dedent(f"""
    Hier ist eine Java-Klasse aus einem produktiven Service.
    Erzeuge eine passende JUnit-5-Testklasse. Anforderungen:

    - Nutze JUnit 5 (`org.junit.jupiter.api.*`).
    - Erzeuge sinnvolle Testmethoden: Normalfall, Edge Cases, Fehlerfälle.
    - Verwende wenn sinnvoll Mockito (`org.mockito.*`) zum Mocking.
    - Stelle sicher, dass der Code kompilierbar ist.
    - Wenn es bereits etablierte Public-Methoden gibt, teste sie explizit.
    - Nutze die gleiche package-Deklaration wie die Quellklasse (aber im Test-Paket).

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
        # einfache Heuristik: package-Zeile am Anfang einfügen
        test_code = f"package {package_name};\n\n{test_code}"

    target_path.write_text(test_code, encoding="utf-8")
    print(f"[OK] Test geschrieben: {target_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, help="Pfad zu src/main/java")
    parser.add_argument("--test-dir", required=True, help="Pfad zu src/test/java")
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source_dir).resolve()
    test_dir = pathlib.Path(args.test_dir).resolve()

    changed_files = get_changed_java_files(source_dir)
    if not changed_files:
        print("[INFO] Keine geänderten Java-Dateien im Source-Verzeichnis gefunden.")
        return

    print("[INFO] Geänderte Java-Dateien:")
    for f in changed_files:
        print(f"  - {f}")

    for f in changed_files:
        generate_test_for_file(f, source_dir, test_dir)


if __name__ == "__main__":
    main()
