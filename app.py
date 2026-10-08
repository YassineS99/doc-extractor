import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError

from docgen import generate_docx
from extractor import extract_spec
from pdf_reader import read_pdf_text
from schema import EquipmentSpec

app = FastAPI(title="Engineering Document Extractor")

DOCX_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def spec_from_upload(file: UploadFile) -> EquipmentSpec:
    """Save the upload, read its text, and return a validated spec."""
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(file.file.read())
    tmp.close()

    try:
        text = read_pdf_text(tmp.name)
    finally:
        os.remove(tmp.name)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text found in this PDF. It may be a scanned image.",
        )

    try:
        return extract_spec(text)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"The AI output failed validation: {e.errors()}",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/")
def home():
    return {"message": "Engineering Document Extractor is running. Open /docs"}


@app.post("/extract", response_model=EquipmentSpec)
def extract(file: UploadFile = File(...)):
    return spec_from_upload(file)


@app.post("/generate")
def generate(file: UploadFile = File(...)):
    spec = spec_from_upload(file)

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    out.close()
    missing = generate_docx(spec, out.name)

    return FileResponse(
        out.name,
        media_type=DOCX_TYPE,
        filename="equipment_spec.docx",
        headers={"X-Missing-Fields": ", ".join(missing) or "none"},
    )