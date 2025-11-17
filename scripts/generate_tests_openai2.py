# -*- coding: utf-8 -*-
import os
import glob
import re
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

# WICHTIG:
# AZURE_OPENAI_ENDPOINT in den Secrets OHNE api-version:
# z.B. https://swc-eh-oai-openai-1.openai.azure.com/
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-04-01-preview",  # aus deiner Endpoint-URL
)

SOURCE_PATTERN = "src/main/java/**/*.java"
TEST_ROOT = "src/test/java"

PROMPT_TEMPLATE = (
    "Erstelle JUnit 5 Tests fuer die folgende Java-Klasse.\n\n"
    "Vorgaben:\n"
    "- Verwende JUnit 5.\n"
    "- Nutze sprechende Testmethodennamen.\n"
    "- Generiere mehrere sinnvolle Testfaelle.\n"
    "- Gib nur reinen Java-Quellcode aus, ohne Erklaerungen, ohne Markdown.\n\n"
    "Klasse:\n\n"
    "{source_code}\n"
)


def extract_text_from_response(resp) -> str:
    """
    Holt den Text aus der Responses-API-Struktur:
    typischerweise resp.output[0].content[0].text.value
    Wir sind defensiv und behandeln sowohl Objekt- als auch Dict-Form.
    """
    try:
        if not hasattr(resp, "output") or not resp.output:
            return ""

        first_output = resp.output[0]
        content_list = getattr(first_output, "content", [])
        texts = []

        for item in content_list:
            # neuer SDK-Typ
            if hasattr(item, "text") and hasattr(item.text, "value"):
                val = item.text.value
                if isinstance(val, str):
                    texts.append(val)
            # dict-basierte Struktur (zur Sicherheit)
            elif isinstance(item, dict):
                tx = item.get("text")
                if isinstance(tx, dict):
                    val = tx.get("value")
                    if isinstance(val, str):
                        texts.append(val)

        return "\n".join(texts).strip()
    except Exception as e:
        print(f"Warnung: Konnte Text aus Response nicht extrahieren: {e}")
        return ""


def clean_java_code(content: str) -> str:
    """
    Entfernt Markdown und alles vor der ersten 'class'-Definition.
    Gibt einen leeren String zurück, wenn es nicht nach Java aussieht.
    """
    if not content:
        return ""

    # Falls in ```java ... ``` eingebettet
    if "```" in content:
        parts = content.split("```")
        for i, p in enumerate(parts):
            if p.strip().startswith("java"):
                if i + 1 < len(parts):
                    content = parts[i + 1]
                break

    # Alles vor 'class' entfernen
    m = re.search(r"\bclass\b", content)
    if not m:
        return ""

    cleaned = content[m.start():].strip()

    # ganz grober Sanity-Check: muss { und } enthalten
    if "{" not in cleaned or "}" not in cleaned:
        return ""

    return cleaned


def generate_test_for_file(java_file: str):
    # Optional: bestimmte Klassen skippen, z.B. Application-Klasse
    if java_file.endswith("Application.java"):
        print(f"Skippe Application-Klasse: {java_file}")
        return

    with open(java_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    prompt = PROMPT_TEMPLATE.format(source_code=source_code)

    print(f"Generating tests for: {java_file}")

    resp = client.responses.create(
        model=deployment,
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
    )

    raw = extract_text_from_response(resp)
    code = clean_java_code(raw)

    if not code:
        print("Keine gueltige Java-Klasse im Response gefunden, ueberspringe Datei.")
        return

    rel_path = os.path.relpath(java_file, "src/main/java")
    pkg_dir = os.path.dirname(rel_path)
    base_name = os.path.splitext(os.path.basename(java_file))[0]
    test_name = base_name + "Test"

    out_dir = os.path.join(TEST_ROOT, pkg_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, test_name + ".java")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(code + "\n")

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
