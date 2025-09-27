from pydantic import BaseModel
from typing import List, Optional, Dict

class TestItem(BaseModel):
    name: str
    value: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    ref_range: Optional[Dict[str, float]] = None

class SimplifyResponse(BaseModel):
    tests: List[TestItem]
    summary: str
    explanations: Optional[List[str]] = []
    status: str

