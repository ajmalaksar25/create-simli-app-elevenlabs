from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from models import (
    StartScreeningRequest,
    StartScreeningResponse,
    SessionContextResponse,
    QuestionsResponse,
    ErrorResponse,
    ScreeningContext
)
from services.resume_processor import ResumeProcessor
from services.langchain_service import LangChainService
from services.session_manager import session_manager
import base64

router = APIRouter(prefix="/api/screening", tags=["screening"])

# Initialize services
resume_processor = ResumeProcessor()
langchain_service = LangChainService()


@router.post("/start", response_model=StartScreeningResponse)
async def start_screening(
    candidate_name: str = Form(...),
    job_description: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None)
):
    """
    Start a new screening session
    
    Accepts either resume_text (plain text) or resume_file (upload)
    """
    try:
        # Process resume
        resume_content = None
        file_extension = None
        
        if resume_file:
            file_content = await resume_file.read()
            resume_content = base64.b64encode(file_content).decode('utf-8')
            file_extension = resume_file.filename.split('.')[-1] if resume_file.filename else None
        elif resume_text:
            resume_content = resume_text
        
        if not resume_content:
            raise HTTPException(status_code=400, detail="Either resume_text or resume_file must be provided")
        
        # Extract resume text
        resume_text_extracted = resume_processor.process_resume(
            resume_text=resume_text if resume_text else None,
            resume_file=resume_content if resume_file else None,
            file_extension=file_extension
        )
        
        # Generate analysis using LangChain
        match_analysis = langchain_service.generate_match_analysis(
            resume_text_extracted,
            job_description
        )
        
        resume_summary = langchain_service.generate_resume_summary(
            resume_text_extracted
        )
        
        screening_questions = langchain_service.generate_screening_questions(
            resume_text_extracted,
            job_description,
            match_analysis
        )
        
        # Create context
        context = ScreeningContext(
            candidate_name=candidate_name,
            job_description=job_description,
            resume_summary=resume_summary,
            match_analysis=match_analysis,
            screening_questions=screening_questions
        )
        
        # Create session
        session_id = session_manager.create_session(context)
        
        return StartScreeningResponse(
            session_id=session_id,
            context=context
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{session_id}/context", response_model=SessionContextResponse)
async def get_session_context(session_id: str):
    """Get formatted context for a screening session"""
    context = session_manager.get_session(session_id)
    
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionContextResponse(
        session_id=session_id,
        context=context
    )


@router.get("/{session_id}/questions", response_model=QuestionsResponse)
async def get_session_questions(session_id: str):
    """Get screening questions for a session"""
    context = session_manager.get_session(session_id)
    
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return QuestionsResponse(
        session_id=session_id,
        questions=context.screening_questions
    )


@router.post("/{session_id}/analyze")
async def reanalyze_session(session_id: str):
    """Re-analyze a session (future enhancement)"""
    context = session_manager.get_session(session_id)
    
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Re-analyze using LangChain
    match_analysis = langchain_service.generate_match_analysis(
        context.resume_summary.condensed_text,
        context.job_description
    )
    
    # Update context
    context.match_analysis = match_analysis
    
    return SessionContextResponse(
        session_id=session_id,
        context=context
    )

