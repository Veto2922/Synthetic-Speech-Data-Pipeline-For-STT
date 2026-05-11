from pydantic import BaseModel
from typing import List, Optional

class ValidationResult(BaseModel):
    audio_id: str
    status: str = "reviewed"
    review_status: str
    duration_seconds: float
    wer: Optional[float] = None
    transcript: Optional[str] = None
    issues: List[str] = []
    validated_at: str
