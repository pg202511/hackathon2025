# -*- coding: utf-8 -*-
import os
import glob
from openai import AzureOpenAI

# Konfiguration aus Umgebungsvariablen
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Deployment-Name aus Azure

if not endpoint or not api_key or not deployment:
    raise SystemExit(
        "Azure OpenAI Konfiguration fehlt: "
        "AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY / AZURE_OPENAI_DEPLOYMENT"
    )

# Achtung: Endpoint OHNE api-version in den Secrets speichern,
# z.B. https://swc-eh-oai-openai-1.openai.azure.com/
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-04-01-preview",  # aus deiner URL
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


def extract_text_from_response(resp) -> str:
    """
    Responses-API Antwort in reinen Text umwandeln.
    Erwartete Struktur: resp.output[0].content[0].text.value
    Wir sind defensive, falls sich die Struktur leicht aendert.
    """
    try:
        # neue SDK-Struktur
        first_output = resp.output[0]
        first_content = first_output.content[0]
        # bei text-basierten Antworten heisst das meistens so:
        if hasattr(first_content, "text") and hasattr(first_content.text, "value"):
            return first_content.text.value
        # Fallback: plain text
        return str(first_content)
    except Exception as e:
        print(f"Warnung: Konnte Text aus Response nicht sauber extrahieren: {e}")
        return str(resp)


def generate_test_for_file(java_file: str):
    with open(java_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    prompt = PROMPT_TEMPLATE.format(source_code=source_code)

    print(f"Generating tests for: {java_file}")

    # Responses API statt chat.completions
    resp = client.responses.create(
        model=deployment,   # Deployment-Name aus Azure
        input=[
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

    content = extract_text_from_response(resp)

    # Java-Code aus ```java ... ```-Block extrahieren, falls vorhanden
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
