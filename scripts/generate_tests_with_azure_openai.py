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
        p = pathlib.P
