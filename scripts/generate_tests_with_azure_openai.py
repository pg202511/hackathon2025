#!/usr/bin/env python3
"""
generate_tests_with_azure_openai.py

Erzeugt oder aktualisiert JUnit-5-Tests für Java-Klassen mittels Azure OpenAI.

- Läuft über ALLE .java-Dateien unterhalb von src/main/java (kein git diff).
- Für Bootstrap-Klassen (z.B. mit @SpringBootApplication oder *Application) werden KEINE Tests erzeugt.
- Für Spring MVC Controller wird empfohlen, im Test direkt den Controller zu instanziieren
  und org.springframework.ui.ExtendedModelMap als Model-Implementierung zu verwenden.

Erwartet folgende Umgebungsvariablen:
- AZURE_OPENAI_ENDPOINT       (z.B. https://<resource>.openai.azure.com)
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT     (Name des Deployments, z.B. gpt-4o, o3-mini, ...)

Aufruf (z.B. im GitHub Workflow):
    python scripts/generate_tests_with_azure_openai.py \
        --source-dir src/main/java \
        --test-dir src/test/java
"""

import os
import pathlib
import textwrap
import json
import re
import argparse
from typing import Optional, Tuple, List

import requests

API_VERSION = "2024-02-15-preview"  # ggf. an deine Azure-OpenAI-Ressource anpassen


# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------
def read_file(path: pathlib.Path) -> str:
    if not path.exists():
        print(f"[WARN] Datei nicht gefunden: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def extract_package_and_class(java_source: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrahiert package-Name und Klassenname aus Java-Quelltext."""
    package_match = re.search(r"package\s+([a-zA-Z0-9_.]+)\s*;", java_source)
    class_match = re.search(r"(public\s+)?class\s+([A-Za-z0-9_]+)", java_source)
    package_name = package_match.group(1) if package_match else None
    class_name = class_match.group(2) if class_match else None
    return package_name, class_name


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
# Azure OpenAI Aufruf
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

    system_prompt = (
        "You are a senior Java developer and test engineer. "
        "Generate high-quality, compilable JUnit 5 test classes. "
        "Focus on meaningful edge cases, null handling, and business rules. "
        "Do NOT change production code; only produce test code. "
        "Use JUnit 5 (org.junit.jupiter.api.*) and, when appropriate, Mockito. "
        "Prefer plain unit tests without starting heavy frameworks when possible. "
        "For Spring MVC controllers, DO NOT load a Spring context; "
        "instantiate the controller directly and use simple Model implementations "
        "like org.springframework.ui.ExtendedModelMap when a method expects "
        "org.springframework.ui.Model."
    )

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        # KEIN max_tokens, KEINE temperature -> kompatibel mit neueren Azure-Modellen
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=90)
    if resp.status_code >= 400:
        raise RuntimeError(f"Azure OpenAI Fehler {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


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
# Testgenerierung für eine Datei
# ---------------------------------------------------------
def generate_test_for_file(
    source_file: pathlib.Path,
    source_dir: pathlib.Path,
    test_dir: pathlib.Path
) -> None:
    java_source = read_file(source_file)
    if not java_source.strip():
        print(f"[WARN] Leere Datei oder nicht lesbar: {source_file}")
        return

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
    Hier ist eine Java-Klasse aus einem Spring Boot / Java-Projekt.
    Erzeuge eine passende JUnit-5-Testklasse. Anforderungen:

    Allgemein:
    - Nutze JUnit 5 (`org.junit.jupiter.api.*`).
    - Erzeuge sinnvolle Testmethoden für öffentliche Methoden:
      - Normalfall
      - Edge Cases
      - Fehlerfälle, soweit ersichtlich.
    - Verwende nach Bedarf Mockito (`org.mockito.*`) zum Mocking.
    - Stelle sicher, dass der Testcode kompilierbar ist und typische Importe enthält.
    - Verändere NICHT den Produktionscode; erzeuge nur Testcode.

    Speziell für Spring MVC Controller:
    - Falls Methoden ein Argument vom Typ `org.springframework.ui.Model` haben:
      - verwende im Test `Model model = new org.springframework.ui.ExtendedModelMap();`
      - rufe die Methode direkt auf, z.B.:
          `String viewName = controller.index(model);`
    - Verwende NICHT `ModelMap`, wenn die Methode `Model` erwartet.
    - Starte keinen Spring ApplicationContext im Test,
      verwende KEINE Annotationen wie `@SpringBootTest`, `@WebMvcTest` oder `@ExtendWith(SpringExtension.class)`,
      außer es ist absolut notwendig (bitte eher vermeiden).
    - Instanziere den Controller direkt mit `new <ClassName>()` oder mit einfachen Konstruktor-Parametern.

    Package / Struktur:
    - Nutze die gleiche package-Deklaration wie die Quellklasse.
    - Die Testklasse soll unter dem entsprechenden Pfad in src/test/java liegen
      (das übernimmt das Skript bereits durch den Pfad).

    Quell-Datei (Pfad): {source_file}
    Quell-Code:
    ---
    {java_source}
    ---
    Gib NUR den Java-Code der Testklasse zurück (keine Erklärungen, keine Kommentare außerhalb von Java).
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
        description="Erzeugt/aktualisiert JUnit-Tests mittels Azure OpenAI für Java-Dateien."
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

    source_dir = pathlib.Path(args.source_dir).resolve()
    test_dir = pathlib.Path(args.test_dir).resolve()

    if not source_dir.exists():
        raise SystemExit(f"Source-Verzeichnis existiert nicht: {source_dir}")

    # Einfachheit für Hackathon: ALLE Java-Dateien unter source_dir
    target_files: List[pathlib.Path] = sorted(source_dir.rglob("*.java"))

    if not target_files:
        print("[INFO] Keine Java-Dateien gefunden – nichts zu tun.")
        return

    print("[INFO] Java-Dateien, für die Tests erzeugt werden:")
    for f in target_files:
        print(f"  - {f}")

    for f in target_files:
        try:
            generate_test_for_file(f, source_dir, test_dir)
        except Exception as e:
            print(f"[ERROR] Fehler beim Generieren von Tests für {f}: {e}")


if __name__ == "__main__":
    main()
