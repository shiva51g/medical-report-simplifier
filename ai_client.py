import os
from typing import List, Dict  # <-- Add this line
from dotenv import load_dotenv

# Load OpenAI key
load_dotenv()
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def generate_patient_friendly_summary(tests: List[Dict]) -> Dict:
    numeric_tests = [t for t in tests if t.get("value") is not None]
    if not numeric_tests:
        return {"summary": "No numeric test values found.", "explanations": [], "status": "unprocessed"}

    if not OPENAI_KEY:  # Mock fallback if API key not found
        summary = ", ".join([f"{t['name']} is {t['status']}" for t in numeric_tests if t.get("status")])
        explanations = []
        for t in numeric_tests:
            if t.get("status") == "low":
                explanations.append(f"Low {t['name'].lower()} may relate to anemia or deficiency.")
            elif t.get("status") == "high":
                explanations.append(f"High {t['name'].lower()} can occur with infection or inflammation.")
        return {"summary": summary or "Tests parsed.", "explanations": explanations, "status": "ok"}

    # Real AI mode
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        tests_str = "; ".join(
            [f"{t['name']}={t['value']}{t.get('unit','')} ({t.get('status','unknown')})" for t in numeric_tests]
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical assistant. Explain lab results simply."},
                {"role": "user", "content": f"Summarize: {tests_str}"}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return {"summary": completion.choices[0].message.content.strip(), "explanations": [], "status": "ok"}
    except Exception as e:
        return {"summary": f"AI error: {str(e)}", "explanations": [], "status": "unprocessed"}
