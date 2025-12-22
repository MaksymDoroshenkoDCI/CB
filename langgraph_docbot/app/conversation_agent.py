"""
Conversational Requirements Agent
Gathers requirements through dialog with the user, reading questions from JSON file.
"""
import json
import os
from typing import Dict, Any, List
from pathlib import Path


def load_dialog_structure() -> Dict[str, Any]:
    """Loads dialog structure from JSON file."""
    current_dir = Path(__file__).parent
    json_path = current_dir / "dialog_structure.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"Dialog structure file not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_questions_from_json() -> List[Dict[str, Any]]:
    """Gets list of questions from JSON structure."""
    structure = load_dialog_structure()
    return structure.get("questions", [])


def get_completion_triggers() -> List[str]:
    """Gets completion trigger phrases from JSON."""
    structure = load_dialog_structure()
    return structure.get("completion_triggers", ["done", "complete", "finish"])


def conversation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Conversational Agent - gathers requirements through dialog.
    Reads questions from dialog_structure.json file.
    
    Logic:
    1. If this is the first step - initializes dialog structure from JSON
    2. If user answered - saves the answer
    3. If there are more questions - shows next question
    4. If all questions collected - forms summary and proceeds to generation
    """
    # Load questions from JSON
    questions = get_questions_from_json()
    completion_triggers = get_completion_triggers()
    
    # Initialize dialog structure if it doesn't exist
    if "answers" not in state:
        state["answers"] = {}
        state["current_question"] = 0
        state["conversation_complete"] = False
        state["collected_requirements"] = None
        state["questions_data"] = questions  # Store questions data
    
    questions_data = state.get("questions_data", questions)
    
    # If user provided an answer
    if state.get("user_input") and state.get("user_input").strip():
        current_q_idx = state.get("current_question", 0)
        
        # Check if user wants to complete the dialog
        user_input_lower = state["user_input"].lower().strip()
        
        if any(trigger in user_input_lower for trigger in completion_triggers):
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
        if current_q_idx < len(questions_data):
            question_obj = questions_data[current_q_idx]
            question_text = question_obj.get("question", "")
            state["answers"][question_text] = state["user_input"]
        
        # Move to next question
        state["current_question"] = current_q_idx + 1
    
    # Check if all questions are collected
    current_q_idx = state.get("current_question", 0)
    
    if current_q_idx >= len(questions_data):
        # All questions collected
        state["conversation_complete"] = True
        summary = _format_requirements_summary(state["answers"])
        state["collected_requirements"] = summary
        state["system_context"] = "ALL_ANSWERS_COLLECTED"
        return state
    
    # Get next question from JSON
    next_question_obj = questions_data[current_q_idx]
    next_question = next_question_obj.get("question", "")
    
    state["system_context"] = next_question
    state["current_question_text"] = next_question
    state["current_question_id"] = next_question_obj.get("id")
    state["current_question_category"] = next_question_obj.get("category")
    
    return state


def _format_requirements_summary(answers: Dict[str, str]) -> str:
    """Forms structured summary from collected answers."""
    summary_parts = ["# Collected System Requirements\n\n"]
    
    for question, answer in answers.items():
        summary_parts.append(f"## {question}\n\n")
        summary_parts.append(f"{answer}\n\n")
    
    return "\n".join(summary_parts)


def all_answers_collected(state: Dict[str, Any]) -> str:
    """
    Conditional function for LangGraph - checks if all answers are collected.
    Returns "continue_conversation" or "generate_docs".
    """
    if state.get("conversation_complete", False):
        return "generate_docs"
    return "continue_conversation"
