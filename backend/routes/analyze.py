from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.nlp_local import analyze_text_local

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze/")
def analyze_text(request: AnalyzeRequest):
    return analyze_text_local(request.text)
