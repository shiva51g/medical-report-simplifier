from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from ocr import extract_lines_from_text, mock_ocr_from_image
from normalize import normalize_tests
from ai_client import generate_patient_friendly_summary

app = FastAPI(title="Medical Report Simplifier", version="2.2")


@app.post("/simplify-report-text")
async def simplify_report_text(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    # OCR / Text extraction
    lines = extract_lines_from_text(text)
    confidence = 0.85 if lines else 0.3

    # Normalization
    tests_normalized, norm_conf = normalize_tests(lines)
    if norm_conf < 0.4:
        return JSONResponse(
            status_code=422,
            content={
                "tests_raw": lines,
                "tests": tests_normalized,
                "summary": "",
                "status": "needs_better_input"
            }
        )

    # AI Summary
    ai_res = generate_patient_friendly_summary(tests_normalized)

    # Guardrail for hallucinated tests
    if not tests_normalized or ai_res.get("status") != "ok":
        return JSONResponse(
            status_code=422,
            content={
                "tests_raw": lines,
                "tests": tests_normalized,
                "summary": ai_res.get("summary", ""),
                "status": "unprocessed",
                "reason": "hallucinated tests not present in input"
            }
        )

    return {
        "tests_raw": lines,
        "tests": tests_normalized,
        "summary": ai_res.get("summary"),
        "explanations": ai_res.get("explanations", []),
        "status": "ok"
    }


@app.post("/simplify-report-image")
async def simplify_report_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="File input is required.")

    contents = await file.read()
    lines, confidence = mock_ocr_from_image(contents)

    if not lines:
        return JSONResponse(
            status_code=422,
            content={
                "tests_raw": [],
                "tests": [],
                "summary": "",
                "status": "unprocessed",
                "reason": "OCR failed or no text detected"
            }
        )

    # Normalization
    tests_normalized, norm_conf = normalize_tests(lines)
    if norm_conf < 0.4:
        return JSONResponse(
            status_code=422,
            content={
                "tests_raw": lines,
                "tests": tests_normalized,
                "summary": "",
                "status": "needs_better_input"
            }
        )

    # AI Summary
    ai_res = generate_patient_friendly_summary(tests_normalized)

    # Guardrail
    if not tests_normalized or ai_res.get("status") != "ok":
        return JSONResponse(
            status_code=422,
            content={
                "tests_raw": lines,
                "tests": tests_normalized,
                "summary": ai_res.get("summary", ""),
                "status": "unprocessed",
                "reason": "hallucinated tests not present in input"
            }
        )

    return {
        "tests_raw": lines,
        "tests": tests_normalized,
        "summary": ai_res.get("summary"),
        "explanations": ai_res.get("explanations", []),
        "status": "ok"
    }


@app.get("/")
async def root():
    return {"message": "Medical Report Simplifier API is running. Visit /docs for demo."}
