import re
from typing import List, Dict, Tuple
import os
from openai import OpenAI
from dotenv import load_dotenv

# ---------------- Load .env ----------------
load_dotenv()
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables or .env file")

client = OpenAI(api_key=OPENAI_KEY)

# ---------------- Reference ranges ----------------
REF_RANGES = {
    "Hemoglobin": {"low": 12.0, "high": 18.0},
    "WBC": {"low": 4000, "high": 11000},
    "RBC": {"low": 4.0, "high": 5.8},
    "Platelets": {"low": 150000, "high": 450000},
}

# ---------------- AI Helpers ----------------
def normalize_name_ai(raw_name: str) -> str:
    """
    Normalize lab test names using OpenAI.
    """
    try:
        prompt = f"Normalize this lab test name to a standard CBC name: '{raw_name}'. Only return the corrected name (e.g., Hemoglobin, WBC, RBC, Platelets)."
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical lab assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        return completion.choices[0].message.content.strip() or raw_name.title()
    except Exception:
        return raw_name.title()

def normalize_status_ai(raw_status: str) -> str:
    """
    Normalize lab test status to low/high/normal using OpenAI.
    """
    if not raw_status:
        return None
    try:
        prompt = f"Correct this lab test status to 'low', 'high', or 'normal': '{raw_status}'"
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical lab assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0
        )
        return completion.choices[0].message.content.strip().lower()
    except Exception:
        return raw_status.lower()

# ---------------- Utility ----------------
def split_multiple_tests(line: str) -> List[str]:
    """
    Split a line into separate test segments, preserving numbers with commas and decimals.
    """
    # Match patterns like "WBC 11,200 /uL" or "Hemoglobin 10.2 g/dL"
    return re.findall(r"[A-Za-z\s]+[0-9][0-9,]*\.?[0-9]*\s*[a-zA-Z/%μuLx\^\d]+(?:/[a-zA-Z]+)?", line)

# ---------------- Normalization ----------------
def normalize_test_line(line: str) -> Tuple[List[Dict], float]:
    results = []
    try:
        segments = split_multiple_tests(line)
        if not segments:
            return ([{"name": line, "value": None, "unit": None, "status": None, "ref_range": None}], 0.6)

        for seg in segments:
            ln = seg.strip()
            status = None

            # Extract status in parentheses
            m_status = re.search(r"\(([^)]+)\)", ln)
            if m_status:
                s = m_status.group(1).strip()
                status = normalize_status_ai(s)
                ln = ln.replace(m_status.group(0), "").strip()

            # Extract value and unit
            m_val = re.search(r"([0-9][0-9,]*\.?[0-9]*)\s*([a-zA-Z/%μuLx\^\d]+(?:/[a-zA-Z]+)?)", ln)
            if m_val:
                value_str = m_val.group(1).replace(",", "")
                value = float(value_str)
                unit = m_val.group(2).strip() if m_val.group(2) else None

                # Extract test name
                parts = ln.split(m_val.group(0), 1)
                name_raw = parts[0].strip(": ").strip()
                name = normalize_name_ai(name_raw)
                ref = REF_RANGES.get(name)

                # Determine status if not provided
                if not status and ref:
                    if value < ref["low"]:
                        status = "low"
                    elif value > ref["high"]:
                        status = "high"
                    else:
                        status = "normal"

                results.append({
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "status": status,
                    "ref_range": ref
                })
            else:
                results.append({
                    "name": ln,
                    "value": None,
                    "unit": None,
                    "status": None,
                    "ref_range": None
                })

        return results, 0.9
    except Exception:
        return ([{"name": line, "value": None, "unit": None, "status": None, "ref_range": None}], 0.3)

def normalize_tests(lines: List[str]) -> Tuple[List[Dict], float]:
    final_results, confidences = [], []
    for ln in lines:
        items, conf = normalize_test_line(ln)
        final_results.extend(items)
        confidences.append(conf)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return final_results, avg_conf
