"""
Conversational Requirements Agent
Gathers requirements through dialog with the user, reading questions from JSON file.
Implements Business Analyst interview style with acknowledgments, transitions, and progress updates.
"""
import json
import os
import random
from typing import Dict, Any, List, Optional
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


def get_opening_message() -> str:
    """Gets opening message from dialog structure."""
    structure = load_dialog_structure()
    return structure.get("opening_message", "Hello! I'll help you create comprehensive technical documentation for your IT system. Let's start!")


def get_acknowledgment() -> str:
    """Gets a random acknowledgment message."""
    structure = load_dialog_structure()
    acknowledgments = structure.get("acknowledgments", ["Great! That's very helpful.", "Excellent! Thank you."])
    return random.choice(acknowledgments)


def get_section_transition(category: str) -> Optional[str]:
    """Gets section transition message for a category."""
    structure = load_dialog_structure()
    transitions = structure.get("section_transitions", {})
    return transitions.get(category)


def get_progress_update(after_question: int) -> Optional[str]:
    """Gets progress update message if available."""
    structure = load_dialog_structure()
    progress_updates = structure.get("progress_updates", [])
    for update in progress_updates:
        if update.get("after_question") == after_question:
            return update.get("message")
    return None


def get_closing_message() -> str:
    """Gets closing message before document generation."""
    structure = load_dialog_structure()
    return structure.get("closing_message", "Excellent! I've gathered all the information I need. Is there anything else you'd like to add?")


def conversation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Conversational Agent - gathers requirements through dialog.
    Implements Business Analyst interview style with:
    - Opening message
    - Acknowledgments after answers
    - Section transitions
    - Progress updates
    - Closing message before generation
    """
    # Load questions from JSON
    questions = get_questions_from_json()
    completion_triggers = get_completion_triggers()
    
    # Initialize dialog structure if it doesn't exist
    is_first_call = "answers" not in state
    if is_first_call:
        state["answers"] = {}
        state["current_question"] = 0
        state["conversation_complete"] = False
        state["collected_requirements"] = None
        state["questions_data"] = questions
        state["user_input"] = ""
        state["show_opening"] = True  # Flag to show opening message
    
    questions_data = state.get("questions_data", questions)
    current_q_idx = state.get("current_question", 0)
    show_opening = state.get("show_opening", False)
    
    # Get user input
    user_input = state.get("user_input", "").strip()
    
    # Check if waiting for confirmation after closing message (MUST be first, before processing user_input)
    if state.get("waiting_for_confirmation", False):
        if user_input:
            # User confirmed (or said no), proceed to generation
            state["conversation_complete"] = True
            if state["answers"]:
                summary = _format_requirements_summary(state["answers"])
                state["collected_requirements"] = summary
            else:
                state["collected_requirements"] = user_input if user_input else ""
            state["system_context"] = "ALL_ANSWERS_COLLECTED"
            state["waiting_for_confirmation"] = False  # Clear flag
            return state
        else:
            # Still waiting for confirmation, show closing message again
            closing_msg = get_closing_message()
            state["current_question_text"] = closing_msg
            state["system_context"] = closing_msg
            state["conversation_complete"] = False
            return state
    
    # If user provided an answer (not empty)
    if user_input:
        # Check if user wants to complete the dialog
        user_input_lower = user_input.lower()
        
        if any(trigger in user_input_lower for trigger in completion_triggers):
            # User wants to complete the dialog
            state["conversation_complete"] = True
            if state["answers"]:
                summary = _format_requirements_summary(state["answers"])
                state["collected_requirements"] = summary
            else:
                state["collected_requirements"] = user_input
            state["system_context"] = "ALL_ANSWERS_COLLECTED"
            return state
        
        # Save answer to current question with acknowledgment
        if current_q_idx < len(questions_data):
            question_obj = questions_data[current_q_idx]
            question_text = question_obj.get("question", "")
            state["answers"][question_text] = user_input
            
            # Store acknowledgment for this answer
            acknowledgment = get_acknowledgment()
            state["last_acknowledgment"] = acknowledgment
        
        # Move to next question
        current_q_idx = current_q_idx + 1
        state["current_question"] = current_q_idx
        state["show_opening"] = False
    
    # Check if all questions are collected
    if current_q_idx >= len(questions_data):
        # All questions answered - automatically complete conversation
        # No need for closing message, UI will show "Generate Documentation" button
        state["conversation_complete"] = True
        if state["answers"]:
            summary = _format_requirements_summary(state["answers"])
            state["collected_requirements"] = summary
        else:
            state["collected_requirements"] = user_input if user_input else ""
        state["system_context"] = "ALL_ANSWERS_COLLECTED"
        state["waiting_for_confirmation"] = False
        return state
    
    # Get next question from JSON
    next_question_obj = questions_data[current_q_idx]
    next_question = next_question_obj.get("question", "")
    category = next_question_obj.get("category", "")
    
    # Build question message with opening, transition, or progress update
    question_message_parts = []
    
    # Add opening message for first question
    if show_opening:
        opening = get_opening_message()
        question_message_parts.append(opening)
        question_message_parts.append("")  # Empty line
        state["show_opening"] = False
    
    # Add acknowledgment from previous answer (only if we just processed an answer)
    # Check if we have a saved acknowledgment from the previous step
    if current_q_idx > 0 and state.get("last_acknowledgment") and not state.get("waiting_for_confirmation", False):
        acknowledgment = state.get("last_acknowledgment")
        question_message_parts.append(acknowledgment)
        question_message_parts.append("")  # Empty line
        
        # Clear acknowledgment after using it (to avoid showing it again)
        state["last_acknowledgment"] = None
        
        # Add section transition if available
        prev_category = questions_data[current_q_idx - 1].get("category", "") if current_q_idx > 0 else ""
        transition = get_section_transition(prev_category)
        if transition:
            question_message_parts.append(transition)
            question_message_parts.append("")  # Empty line
    
    # Add progress update if available
    progress_update = get_progress_update(current_q_idx)
    if progress_update:
        question_message_parts.append(progress_update)
        question_message_parts.append("")  # Empty line
    
    # Add the actual question
    question_message_parts.append(next_question)
    
    # Combine all parts
    full_question = "\n".join(question_message_parts)
    
    state["system_context"] = full_question
    state["current_question_text"] = full_question
    state["current_question_id"] = next_question_obj.get("id")
    state["current_question_category"] = category
    state["conversation_complete"] = False
    state["waiting_for_confirmation"] = False
    
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
