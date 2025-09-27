import re
from typing import List, Tuple
import numpy as np
from PIL import Image
from io import BytesIO
import easyocr

def extract_lines_from_text(text: str) -> List[str]:
    """
    Split text into lines for normalization.
    **Do not split on commas**, as numeric values may contain them (e.g., 11,200).
    """
    lines = re.split(r'[;\n\r]+', text)
    return [ln.strip() for ln in lines if ln.strip()]

def mock_ocr_from_image(file_bytes) -> Tuple[List[str], float]:
    """
    Extract text from uploaded image using EasyOCR.
    Returns lines and confidence score.
    """
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        img = Image.open(BytesIO(file_bytes))
        result = reader.readtext(np.array(img), detail=0)
        lines = extract_lines_from_text(" ".join(result))
        return lines, 0.85 if lines else 0.3
    except Exception as e:
        return [f"OCR failed: {str(e)}"], 0.2
