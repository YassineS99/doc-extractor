import os
import json
import time
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

from schema import EquipmentSpec
from pdf_reader import read_pdf_text

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Tried in order. Each model has its own free daily quota.
MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
]
BUSY_TRIES = 3
CACHE_DIR = Path("cache")

PROMPT = """You are an engineering document assistant.
Extract the equipment specification from the document below.

Rules:
- Only use information that is written in the document.
- If a value is not in the document, use null. Never guess.
- Convert units: power in kW, voltage in V, weight in kg, temperature in deg C.
- List every standard mentioned by its code only (for example "ISO 9906").
- Return only JSON that follows this schema:

{schema}

DOCUMENT:
{document}
"""


def call_gemini(prompt):
    """Try each model in turn. Retry only when a model is busy (5xx)."""
    last_error = None
    for model in MODELS:
        for attempt in range(1, BUSY_TRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                print(f"Used model: {model}")
                return response.text
            except (errors.ServerError, errors.ClientError) as e:
                last_error = e
                code = getattr(e, "code", None)

                if code in (500, 502, 503, 504):  # server busy
                    if attempt < BUSY_TRIES:
                        wait = 5 * attempt
                        print(f"{model} busy (try {attempt}/{BUSY_TRIES}). Waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    print(f"{model} still busy. Trying next model...")
                    break

                if code in (404, 429):  # not available / quota used up
                    print(f"{model} not usable (error {code}). Trying next model...")
                    break

                raise  # any other error (for example a wrong key): stop now

    raise RuntimeError(f"All models failed. Last error: {last_error}")


def extract_spec(text, use_cache=True):
    """Return a validated EquipmentSpec. Uses a saved result if we have one."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{key}.json"

    if use_cache and cache_file.exists():
        print("Using cached result (no Gemini call).")
        return EquipmentSpec.model_validate_json(
            cache_file.read_text(encoding="utf-8")
        )

    schema_text = json.dumps(EquipmentSpec.model_json_schema())
    prompt = PROMPT.format(schema=schema_text, document=text)
    raw_json = call_gemini(prompt)

    # Pydantic checks the AI answer. Bad data raises an error here.
    spec = EquipmentSpec.model_validate_json(raw_json)

    cache_file.write_text(spec.model_dump_json(indent=2), encoding="utf-8")
    return spec


if __name__ == "__main__":
    text = read_pdf_text("sample_datasheet.pdf")
    # use_cache=False forces a real Gemini call, so this file works as a live test
    spec = extract_spec(text, use_cache=False)
    print(spec.model_dump_json(indent=2))