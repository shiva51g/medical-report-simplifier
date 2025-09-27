Here’s a clean **README.md** for your medical report simplifier project:

````markdown
# Medical Report Simplifier

A backend service that takes medical reports (typed or scanned) and produces **patient-friendly explanations**. The service handles OCR errors, normalizes tests, and ensures no hallucinated results are added. Final output includes **normalized lab tests** and **simplified explanations**.

## Features

- Extract lab test values from **typed or scanned medical reports**.
- Normalize test names, units, reference ranges, and statuses.
- Handle OCR errors and minor typos.
- Produce patient-friendly summaries without hallucinations.
- Works for common tests like:
  - Hemoglobin (Hb)
  - White Blood Cells (WBC)
  - Red Blood Cells (RBC)
  - Platelets

## Tech Stack

- **Python 3.11+**
- **FastAPI** for backend API
- **Pydantic** for data validation
- **OpenAI API** (optional) for generating patient-friendly summaries
- **Regex** and custom logic for test normalization

## Setup

1. Clone the repository:
```bash
git clone https://github.com/shiva51g/medical-report-simplifier.git
cd medical-report-simplifier
````

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add your `.env` file (for API keys or secrets):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

* `POST /simplify-report-text` – Send a typed report and get normalized tests with a summary.
* `POST /simplify-report-image` – Send an image report (OCR) and get normalized tests with a summary.

### Example Input

```json
{
  "report_text": "Hemoglobin 10.2 g/dL, WBC 11,200 /uL, RBC 4.5 x10^12/L, Platelets 300,000 /uL"
}
```

### Example Output

```json
{
  "tests": [
    {"name":"Hemoglobin","value":10.2,"unit":"g/dL","status":"low","ref_range":{"low":12,"high":18}},
    {"name":"WBC","value":11200,"unit":"/uL","status":"high","ref_range":{"low":4000,"high":11000}},
    {"name":"RBC","value":4.5,"unit":"x10^12/L","status":"normal","ref_range":{"low":4,"high":5.8}},
    {"name":"Platelets","value":300000,"unit":"/uL","status":"normal","ref_range":{"low":150000,"high":450000}}
  ],
  "summary": "Low hemoglobin and high white blood cell count.",
  "status":"ok"
}
```
