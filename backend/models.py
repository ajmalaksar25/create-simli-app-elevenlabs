from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum


class ResumeInputType(str, Enum):
    FILE = "file"
    TEXT = "text"


class StartScreeningRequest(BaseModel):
    candidate_name: str = Field(..., description="Name of the candidate")
    job_description: str = Field(..., description="Full job description text")
    resume_text: Optional[str] = Field(None, description="Resume as plain text")
    resume_file: Optional[str] = Field(None, description="Resume file content (base64 encoded)")


class MatchAnalysis(BaseModel):
    compatibility_score: float = Field(..., ge=0, le=100, description="Match score out of 100")
    key_strengths: List[str] = Field(..., description="Key strengths aligning with JD")
    key_gaps: List[str] = Field(..., description="Areas where candidate may lack requirements")
    summary: str = Field(..., description="Overall compatibility summary")


class ResumeSummary(BaseModel):
    key_points: List[str] = Field(..., description="3-5 key points from resume")
    condensed_text: str = Field(..., description="Condensed resume summary")


class ScreeningContext(BaseModel):
    candidate_name: str
    job_description: str
    resume_summary: ResumeSummary
    match_analysis: MatchAnalysis
    screening_questions: List[str] = Field(..., description="List of questions to ask")


class StartScreeningResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    context: ScreeningContext


class SessionContextResponse(BaseModel):
    session_id: str
    context: ScreeningContext


class QuestionsResponse(BaseModel):
    session_id: str
    questions: List[str]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

