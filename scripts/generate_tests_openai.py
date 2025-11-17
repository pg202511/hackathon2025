import os
import glob
import openai

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise SystemExit("OPENAI_API_KEY ist nicht gesetzt")
openai.api_key = api_key

SOURCE_PATTERN = "src/main/java/**/*.java"
TEST_ROOT = "src/test/java"

PROMPT_TEMPLATE = """Erstelle JUnit 5 Tests für die folgende Java-Klasse.

Vorgaben:
- Verwende JUnit 5.
- Nutze sprechende Testmethodennamen.
- Generiere mehrere sinnvolle Testfälle.
- Gib nur reinen Java-Code aus (keine Erklärungen).

Klasse:

```java
{source_code}
```
"""


def generate_test_for_file(java_file: str):
    with open(java_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    prompt = PROMPT_TEMPLATE.format(source_code=source_code)

    print(f"? Generiere Tests für: {java_file}")

    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Du erzeugst JUnit-5-Tests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response["choices"][0]["message"]["content"]

    if "```" in content:
        parts = content.split("```")
        for i, p in enumerate(parts):
            if p.strip().startswith("java"):
                content = parts[i + 1].strip()
                break

    rel_path = os.path.relpath(java_file, "src/main/java")
    pkg_dir = os.path.dirname(rel_path)
    base_name = os.path.splitext(os.path.basename(java_file))[0]
    test_name = base_name + "Test"

    out_dir = os.path.join(TEST_ROOT, pkg_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, test_name + ".java")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print(f"? Test generiert: {out_file}")


def main():
    for java_file in glob.glob(SOURCE_PATTERN, recursive=True):
        generate_test_for_file(java_file)

if __name__ == "__main__":
    main()
