# Engineering Document Extractor

An AI-powered API that reads an engineering datasheet (PDF), extracts the key specifications with an LLM, validates them, and generates a clean Word document. Fields that are missing in the source are flagged for human review instead of being guessed.

## What it does

1. **Extract**: reads text from a PDF and asks Gemini for the specs as JSON.
2. **Validate**: Pydantic checks every field (types, positive values). Bad AI output is rejected.
3. **Generate**: builds a Word document from the validated data.
4. **Flag**: anything not found in the document is marked "Not found in document" and listed under "Review needed".

## Tech stack

Python, FastAPI, Pydantic, Google Gemini API (google-genai), pypdf, python-docx

## Reliability features

- Prompt rule: use `null` for missing values, never guess
- Retries with waiting when the model is busy (5xx errors)
- Automatic fallback across several Gemini models when one is unavailable or out of quota
- Local cache: the same document is never sent to the LLM twice
- Clear API errors for non-PDF files, scanned PDFs (no text layer), and failed validation

## Run it

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file with your key:

```
GEMINI_API_KEY=your_key_here
```

Create the sample PDFs and start the server:

```powershell
python make_sample.py
python make_sample2.py
uvicorn app:app --reload
```

Open http://127.0.0.1:8000/docs and try:

- `POST /extract`: upload a PDF, get validated JSON
- `POST /generate`: upload a PDF, download a Word document. The `X-Missing-Fields` response header lists fields that were not found.

## Project files

| File | Purpose |
| --- | --- |
| `schema.py` | Pydantic model of the fields to extract |
| `pdf_reader.py` | PDF text extraction |
| `extractor.py` | Gemini call, retries, model fallback, cache |
| `docgen.py` | Word document generation |
| `app.py` | FastAPI endpoints |

## Tested with

Two generated sample datasheets: one complete, and one with missing fields to confirm the app flags gaps instead of inventing values. This is a small prototype and has not been evaluated on a large set of real documents.

## Limitations and next steps

- Scanned PDFs need OCR (for example Tesseract) before extraction
- Add a labeled test set of real datasheets to measure extraction accuracy
- Support more document types and a configurable schema
- Add Docker and automated tests