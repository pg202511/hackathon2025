# -*- coding: utf-8 -*-
import os
import glob
import textwrap

from openai import AzureOpenAI

# Konfiguration aus Umgebungsvariablen
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not endpoint or not api_key or not deployment:
    raise SystemExit("Azure OpenAI Konfiguration (AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY / AZURE_OPENAI_DEPLOYMENT) ist nicht vollstaendig gesetzt.")

# Azure OpenAI Client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-10-21",  # ggf. an deine Azure-API-Version anpassen
)

SOURCE_PATTERN = "src/main/java/**/*.java"
TEST_ROOT = "src/test/java"

PROMPT_TEMPLATE = (
    "Erstelle JUnit 5 Tests fuer die folgende Java-Klasse.\n\n"
    "Vorgaben:\n"
    "- Verwende JUnit 5.\n"
    "- Nutze sprechende Testmethodennamen.\n"
    "- Generiere mehrere sinnvolle Testfaelle.\n"
    "- Gib nur reinen Java-Code aus (keine Erklaerungen).\n\n"
    "Klasse:\n\n"
    "{source_code}\n"
)


def generate_test_for_file(java_file: str):
    with open(java_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    prompt = PROMPT_TEMPLATE.format(source_code=source_code)

    print(f"Generating tests for: {java_file}")

    response = client.chat.completions.create(
        model=deployment,  # bei Azure ist das der Deployment-Name
        messages=[
            {
                "role": "system",
                "content": "Du erzeugst saubere, kompakte JUnit-5-Tests in Java.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # Falls der Code in ```java ... ```-Blocks kommt, extrahieren
    if "```" in content:
        parts = content.split("```")
        for i, p in enumerate(parts):
            if p.strip().startswith("java"):
                if i + 1 < len(parts):
                    content = parts[i + 1].strip()
                break

    # Zielpfad: src/test/java/<package>/<ClassName>Test.java
    rel_path = os.path.relpath(java_file, "src/main/java")
    pkg_dir = os.path.dirname(rel_path)
    base_name = os.path.splitext(os.path.basename(java_file))[0]
    test_name = base_name + "Test"

    out_dir = os.path.join(TEST_ROOT, pkg_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, test_name + ".java")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print(f"Test written: {out_file}")


def main():
    files = glob.glob(SOURCE_PATTERN, recursive=True)
    if not files:
        print("No Java source files found.")
        return

    for java_file in files:
        generate_test_for_file(java_file)


if __name__ == "__main__":
    main()
