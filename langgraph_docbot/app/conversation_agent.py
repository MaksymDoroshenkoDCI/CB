"""
Conversational Requirements Agent
Gathers requirements through dialog with the user before documentation generation.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List
from .config import settings


# Default questions for requirements gathering
DEFAULT_QUESTIONS = [
    "Describe the main purpose of the system. What should it do?",
    "Who are the main users of the system? Who is it intended for?",
    "What key features should be implemented? Describe the main capabilities.",
    "What technologies are planned? (programming languages, frameworks, databases)",
    "What integrations are needed? (external APIs, services, systems)",
    "What are the security requirements? (authentication, authorization, data protection)",
    "Describe the system architecture. What are the main components?",
    "What are the deployment and infrastructure requirements?",
]


def get_llm():
    """Returns configured LLM for question generation."""
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def conversation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Conversational Agent - gathers requirements through dialog.
    
    Logic:
    1. If this is the first step - initializes dialog structure
    2. If user answered - saves the answer
    3. If there are more questions - generates next question
    4. If all questions collected - forms summary and proceeds to generation
    """
    # Initialize dialog structure if it doesn't exist
    if "answers" not in state:
        state["answers"] = {}
        state["current_question"] = 0
        state["conversation_complete"] = False
        state["collected_requirements"] = None
    
    # If user provided an answer
    if state.get("user_input") and state.get("user_input").strip():
        current_q_idx = state.get("current_question", 0)
        
        # Check if user wants to complete the dialog
        user_input_lower = state["user_input"].lower().strip()
        skip_phrases = ["done", "complete", "finish", "ready", "generate", "create documentation", "all set"]
        
        if any(phrase in user_input_lower for phrase in skip_phrases):
            # User wants to complete the dialog
            state["conversation_complete"] = True
            # Form summary from collected answers
            if state["answers"]:
                summary = _format_requirements_summary(state["answers"])
                state["collected_requirements"] = summary
                state["system_context"] = "ALL_ANSWERS_COLLECTED"
            else:
                # If no answers, use user_input as single requirement
                state["collected_requirements"] = state["user_input"]
                state["system_context"] = "ALL_ANSWERS_COLLECTED"
            return state
        
        # Save answer to current question
        if current_q_idx < len(DEFAULT_QUESTIONS):
            question = DEFAULT_QUESTIONS[current_q_idx]
            state["answers"][question] = state["user_input"]
        
        # Move to next question
        state["current_question"] = current_q_idx + 1
    
    # Check if all questions are collected
    current_q_idx = state.get("current_question", 0)
    
    if current_q_idx >= len(DEFAULT_QUESTIONS):
        # All questions collected
        state["conversation_complete"] = True
        summary = _format_requirements_summary(state["answers"])
        state["collected_requirements"] = summary
        state["system_context"] = "ALL_ANSWERS_COLLECTED"
        return state
    
    # Generate next question (can use LLM for adaptive questions)
    next_question = DEFAULT_QUESTIONS[current_q_idx]
    
    # Can add context from previous answers for smarter questions
    if state.get("answers"):
        next_question = _generate_contextual_question(
            current_q_idx, 
            state["answers"], 
            DEFAULT_QUESTIONS
        )
    
    state["system_context"] = next_question
    state["current_question_text"] = next_question
    
    return state


def _format_requirements_summary(answers: Dict[str, str]) -> str:
    """Forms structured summary from collected answers."""
    summary_parts = ["# Collected System Requirements\n"]
    
    for question, answer in answers.items():
        summary_parts.append(f"## {question}\n")
        summary_parts.append(f"{answer}\n\n")
    
    return "\n".join(summary_parts)


def _generate_contextual_question(
    current_index: int, 
    previous_answers: Dict[str, str], 
    default_questions: List[str]
) -> str:
    """
    Generates contextual question based on previous answers.
    If LLM is unavailable or error occurs - returns default question.
    """
    try:
        llm = get_llm()
        
        # Form context from previous answers
        context = "\n".join([
            f"Question: {q}\nAnswer: {a}\n"
            for q, a in previous_answers.items()
        ])
        
        prompt = f"""You are an experienced systems analyst who gathers requirements for IT systems.

Based on the user's previous answers, formulate the next question that will help gather more information about the system.

PREVIOUS ANSWERS:
{context}

DEFAULT QUESTION (use as basis if needed):
{default_questions[current_index] if current_index < len(default_questions) else ""}

Question requirements:
- Question should be specific and clear
- Should help gather important information for technical documentation
- Can reference previous answers for clarification
- Should be in English

Return ONLY the question without additional comments."""
        
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        # In case of error return default question
        print(f"Error generating contextual question: {e}")
        if current_index < len(default_questions):
            return default_questions[current_index]
        return "Is there any other important information about the system that should be included in the documentation?"


def all_answers_collected(state: Dict[str, Any]) -> str:
    """
    Conditional function for LangGraph - checks if all answers are collected.
    Returns "continue_conversation" or "generate_docs".
    """
    if state.get("conversation_complete", False):
        return "generate_docs"
    return "continue_conversation"

