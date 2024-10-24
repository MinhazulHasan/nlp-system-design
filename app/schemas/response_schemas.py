from pydantic import BaseModel
from typing import Dict, List

class MetricResponse(BaseModel):
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    total_documents: int
    valid_documents: int
    invalid_documents: int

class ReportResponse(BaseModel):
    metrics: Dict[str, MetricResponse]
    report_path: str