from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agents.safety_reasoning_agent import SafetyReasoningAgent

router = APIRouter()
agent = SafetyReasoningAgent()


class SafetyAnalysisRequest(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    time_of_day: Optional[str] = None
    route_name: Optional[str] = None
    location_label: Optional[str] = None


class SafetyAnalysisResponse(BaseModel):
    risk_level: str
    explanation: str
    recommendation: str


@router.post("/analyze", response_model=SafetyAnalysisResponse)
async def analyze_safety(request: SafetyAnalysisRequest):
    """
    Analyze safety risk using AI reasoning agent.
    """
    try:
        result = agent.analyze_safety_risk(
            risk_score=request.risk_score,
            time_of_day=request.time_of_day,
            route_name=request.route_name,
            location_label=request.location_label
        )
        
        return SafetyAnalysisResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety analysis failed: {str(e)}")