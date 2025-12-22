from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class DocState:
    user_input: str
    project_name: Optional[str] = None
    system_context: Optional[str] = None
    history: List[Dict] = field(default_factory=list)
    session_id: Optional[str] = None
    # Fields for conversational agent
    answers: Optional[Dict[str, str]] = None
    current_question: Optional[int] = None
    current_question_text: Optional[str] = None
    current_question_id: Optional[int] = None
    current_question_category: Optional[str] = None
    questions_data: Optional[List[Dict]] = None
    conversation_complete: Optional[bool] = None
    collected_requirements: Optional[str] = None
    # Fields for documentation
    documentation: Optional[str] = None
    doc_path: Optional[str] = None
    error: Optional[str] = None

