from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Optional, Dict, Any
import traceback
from app.graph import workflow
from app.validators import validate_user_input
from app.state import DocState
from app.session_store import get_session, save_session, create_session, delete_session

app = FastAPI(title="LangGraph DocBot", debug=True)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "LangGraph DocBot API",
        "status": "running",
        "endpoints": {
            "generate": "/generate",
            "conversation_start": "/conversation/start",
            "conversation_continue": "/conversation/continue",
            "conversation_generate": "/conversation/generate",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


class GenerateRequest(BaseModel):
    query: str
    project_name: Optional[str] = None
    session_id: Optional[str] = None


class GenerateResponse(BaseModel):
    session_id: str
    outline: str
    documentation: str
    message: str


# Models for conversational API
class ConversationStartRequest(BaseModel):
    project_name: Optional[str] = None
    session_id: Optional[str] = None


class ConversationStartResponse(BaseModel):
    session_id: str
    question: str
    message: str
    conversation_started: bool


class ConversationContinueRequest(BaseModel):
    session_id: str
    answer: str


class ConversationContinueResponse(BaseModel):
    session_id: str
    question: Optional[str] = None
    message: str
    conversation_complete: bool
    collected_requirements: Optional[str] = None


class ConversationGenerateRequest(BaseModel):
    session_id: str
    force: bool = False  # If True, completes dialog even if not all questions are collected


class ConversationGenerateResponse(BaseModel):
    session_id: str
    documentation: str
    doc_path: Optional[str] = None
    message: str


@app.post("/generate", response_model=GenerateResponse)
def generate_doc(req: GenerateRequest):
    """
    Generates documentation directly (without dialog).
    Note: This endpoint now uses the conversation workflow with a single answer.
    For full dialog mode use /conversation/* endpoints.
    """
    try:
        is_valid, error_msg = validate_user_input(req.query)
        if not is_valid:
            sid = req.session_id or str(uuid.uuid4())
            return GenerateResponse(
                session_id=sid,
                outline="",
                documentation="",
                message=error_msg or "",
            )

        session_id = req.session_id or str(uuid.uuid4())
        # Use workflow with single answer (skip dialog)
        init_state = {
            "user_input": req.query,
            "project_name": req.project_name,
            "session_id": session_id,
            "history": [],
            "system_context": None,
            "conversation_complete": True,  # Skip dialog
            "collected_requirements": req.query,  # Use query as requirements
        }

        result = workflow.invoke(init_state)

        # Result is a dict, so we access it as dict
        return GenerateResponse(
            session_id=session_id,
            outline="",  # No outline in simplified workflow
            documentation=result.get("documentation") or "",
            message="Documentation generated and saved to txt file.",
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in generate_doc: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Error generating documentation. Check server logs.",
                "traceback": error_trace if app.debug else None
            }
        )


@app.post("/conversation/start", response_model=ConversationStartResponse)
def start_conversation(req: ConversationStartRequest):
    """Starts a new dialog for requirements gathering."""
    try:
        session_id = req.session_id or str(uuid.uuid4())
        
        # Create initial state
        init_state = {
            "user_input": "",  # Empty at start
            "project_name": req.project_name,
            "session_id": session_id,
            "history": [],
            "system_context": None,
            "answers": {},
            "current_question": 0,
            "current_question_text": None,
            "conversation_complete": False,
            "collected_requirements": None,
        }
        
        # Run workflow to get first question
        result = workflow.invoke(init_state)
        
        # Save session state
        create_session(session_id, result)
        
        question = result.get("current_question_text") or result.get("system_context") or "Describe the main purpose of the system."
        
        return ConversationStartResponse(
            session_id=session_id,
            question=question,
            message="Dialog started. Answer questions to gather requirements.",
            conversation_started=True
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in start_conversation: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Error starting conversation.",
                "traceback": error_trace if app.debug else None
            }
        )


@app.post("/conversation/continue", response_model=ConversationContinueResponse)
def continue_conversation(req: ConversationContinueRequest):
    """Continues dialog with user's answer."""
    try:
        # Get session state
        session_state = get_session(req.session_id)
        if not session_state:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Start a new dialog via /conversation/start"
            )
        
        # Update user_input with answer
        session_state["user_input"] = req.answer
        
        # Continue workflow
        result = workflow.invoke(session_state)
        
        # Save updated state
        save_session(req.session_id, result)
        
        # Check if dialog is complete
        conversation_complete = result.get("conversation_complete", False)
        collected_requirements = result.get("collected_requirements")
        
        if conversation_complete:
            return ConversationContinueResponse(
                session_id=req.session_id,
                question=None,
                message="All requirements collected! You can now generate documentation via /conversation/generate",
                conversation_complete=True,
                collected_requirements=collected_requirements
            )
        else:
            next_question = result.get("current_question_text") or result.get("system_context")
            return ConversationContinueResponse(
                session_id=req.session_id,
                question=next_question,
                message="Answer saved. Continue the dialog.",
                conversation_complete=False,
                collected_requirements=None
            )
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in continue_conversation: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Error continuing conversation.",
                "traceback": error_trace if app.debug else None
            }
        )


@app.post("/conversation/generate", response_model=ConversationGenerateResponse)
def generate_from_conversation(req: ConversationGenerateRequest):
    """Generates documentation based on collected requirements from dialog."""
    try:
        # Get session state
        session_state = get_session(req.session_id)
        if not session_state:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Start a new dialog via /conversation/start"
            )
        
        # If dialog not complete and force - complete it
        if not session_state.get("conversation_complete", False) and req.force:
            session_state["conversation_complete"] = True
            if session_state.get("answers"):
                from app.conversation_agent import _format_requirements_summary
                session_state["collected_requirements"] = _format_requirements_summary(session_state["answers"])
            else:
                session_state["collected_requirements"] = session_state.get("user_input", "")
            session_state["system_context"] = "ALL_ANSWERS_COLLECTED"
        
        # Check if collected requirements exist
        if not session_state.get("collected_requirements") and not session_state.get("conversation_complete"):
            raise HTTPException(
                status_code=400,
                detail="Dialog not completed. Complete the dialog or use force=true"
            )
        
        # Run workflow for documentation generation
        # Set conversation_complete to proceed to generation
        session_state["conversation_complete"] = True
        if not session_state.get("collected_requirements"):
            session_state["collected_requirements"] = session_state.get("user_input", "")
        
        result = workflow.invoke(session_state)
        
        # Delete session after generation (optional)
        # delete_session(req.session_id)
        
        return ConversationGenerateResponse(
            session_id=req.session_id,
            documentation=result.get("documentation") or "",
            doc_path=result.get("doc_path"),
            message="Documentation generated and saved to txt file.",
        )
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in generate_from_conversation: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Error generating documentation.",
                "traceback": error_trace if app.debug else None
            }
        )

