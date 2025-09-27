# Medical Report Simplifier (FastAPI)

This is a complete starter project for **Problem 7: AI-Powered Medical Report Simplifier** 

## What is included
- FastAPI backend with endpoints:
  - `POST /ocr-extract` - accepts `text` or `file` (image/pdf) and returns `tests_raw` (mock or OCR).
  - `POST /normalize-tests` - normalizes raw test lines into structured test objects.
  - `POST /generate-summary` - generates a patient-friendly summary and explanations (uses AI client; mocked if no API key).
  - `POST /simplify-report` - orchestrates the full pipeline (OCR -> normalize -> summary).

- Simple OCR fallback (uses pytesseract if available; otherwise parses provided text).
- AI client wrapper that uses OpenAI if `OPENAI_API_KEY` is set; otherwise returns deterministic mock output.
- Pydantic models and robust error handling + guardrails (hallucination check, confidence thresholds).

## How to run locally (Linux/macOS)

1. Create a virtual env & install:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Install Tesseract for OCR:
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

3. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

4. Test with curl/Postman using `example_request.json` or the endpoints below.

## Example requests

- OCR Extract (text)
```bash
curl -X POST "http://localhost:8000/ocr-extract" -H "Content-Type: application/json" -d @example_request.json
```

- Simplify report (chained)
```bash
curl -X POST "http://localhost:8000/simplify-report" -H "Content-Type: application/json" -d @example_request.json
```

## Notes on AI usage
- Set `OPENAI_API_KEY` environment variable to enable real AI summarization.
- If no key is present, the server returns a safe deterministic mock summary for demonstration/testing.
