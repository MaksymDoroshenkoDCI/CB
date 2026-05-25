import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

def load_dialog_structure() -> Dict[str, Any]:
    """Loads dialog structure from JSON file."""
    # current file is in app/
    file_path = Path(__file__).parent / "dialog_structure.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dialog structure: {e}")
        return {}

def format_requirements(answers: Dict[str, str], questions: List[Dict[str, Any]]) -> str:
    """Formats collected answers into a readable requirements summary."""
    summary = ""
    for q in questions:
        q_id = str(q["id"])
        if q_id in answers:
            summary += f"**{q['question']}**\n{answers[q_id]}\n\n"
    return summary

def conversation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages the conversation flow:
    1. Loads questions if needed
    2. Processes user answer
    3. Selects next question
    """
    if state.get("conversation_complete"):
        return state

    # 1. Initialize logic
    dialog_data = load_dialog_structure()
    questions = dialog_data.get("questions", [])
    
    if "answers" not in state or state["answers"] is None:
        state["answers"] = {}
        
    if "questions_data" not in state or state["questions_data"] is None:
        state["questions_data"] = questions
        
    current_q_index = state.get("current_question", 0)
    if current_q_index is None: 
        current_q_index = 0
        
    user_input = state.get("user_input", "")
    
    # 2. Process Answer (if this is not the first start, i.e., we have input and a current question)
    # logic: if we asked Q1, and user provided input, save it as answer to Q1.
    # But wait, initially current_question might be 0 (first question).
    # If user_input is present and we are 'start'ing, maybe it's the project name or initial prompt?
    # In 'start' endpoint, user_input might be empty or project name.
    
    # Let's assume:
    # - If "current_question_text" is set, it means we already asked a question, and user_input is the answer.
    # - EXCEPT if it's the very first run (session start).
    
    questions_list = state["questions_data"]
    total_questions = len(questions_list)
    
    # If we have a previously asked question, save the answer
    if state.get("current_question_text") and user_input:
        # Save answer for the *current* question index
        # Note: current_question index points to the question we *just asked* or *are about to ask*?
        # Usually easier if current_q_index points to the question we need to ask. 
        # So if we are processing an answer, it's for the question we asked previously.
        # But let's look at how we update:
        # If we just started, current_q_index = 0. We haven't asked Q0 yet. We return Q0.
        # User answers. We receive answer. We save answer for Q0. Increment index to 1. Return Q1.
        
        # We need to distinguish "Starting" from "Answering".
        # State usually persists.
        # If we rely on graph.py, it calls conversation_agent.
        
        # Simple Logic:
        # We will track which question to ask in `current_question`.
        # usage: 
        # 1. Start: current_question=0, answers={}. Return question 0.
        # 2. User replies "My app": user_input="My app".
        #    We see current_question=0. We save input to answer[0].
        #    Increment current_question=1.
        #    Return question 1.
        
        # However, we must ensure we don't save "start" or empty input as answer to Q0 before asking it.
        # The 'start' endpoint likely initializes the state.
        pass

    # This part is tricky without seeing how the API behaves, but let's implement standard flow.
    # We will use 'current_question_id' to track.
    
    # Check if we are "continuing" (user provided answer)
    answered = False
    if state.get("current_question_text") and user_input:
        # We assume user_input is the answer to the current question
        q_idx = state.get("current_question", 0)
        if 0 <= q_idx < total_questions:
            q_data = questions_list[q_idx]
            q_id = str(q_data["id"])
            state["answers"][q_id] = user_input
            
            # Add to history
            if "history" not in state: state["history"] = []
            state["history"].append({"role": "user", "content": user_input})
            
            answered = True
    
    # If we just answered, move to next question
    if answered:
        state["current_question"] = state.get("current_question", 0) + 1
        
    # Select next question
    next_q_idx = state.get("current_question", 0)
    
    if next_q_idx < total_questions:
        # Prepare next question
        q_data = questions_list[next_q_idx]
        state["current_question_text"] = q_data["question"]
        state["current_question_id"] = q_data["id"]
        state["current_question_category"] = q_data["category"]
        state["conversation_complete"] = False
        
        # Add system message to history if it's new
        # (avoid duplicating if we are just re-rendering)
        # But in a graph node, we produce output.
        if "history" not in state: state["history"] = []
        state["history"].append({"role": "system", "content": q_data["question"]})
        
    else:
        # No more questions
        state["conversation_complete"] = True
        state["current_question_text"] = None
        
        # Finalize
        state["collected_requirements"] = format_requirements(state["answers"], questions_list)
        msg = dialog_data.get("closing_message", "Thank you, gathering requirements complete.")
        state["history"].append({"role": "system", "content": msg})

    return state


def get_questions_from_json() -> List[Dict[str, Any]]:
    """Returns list of questions from JSON configuration."""
    data = load_dialog_structure()
    return data.get("questions", [])


def get_opening_message() -> str:
    """Returns the opening message from JSON configuration."""
    data = load_dialog_structure()
    return data.get("opening_message", "Hello! Let's start gathering requirements.")


def _format_requirements_summary(answers: Dict[str, str]) -> str:
    """Internal helper to format requirements summary."""
    questions = get_questions_from_json()
    return format_requirements(answers, questions)


def all_answers_collected(state: Dict[str, Any]) -> str:
    """
    Conditional edge function.
    Returns:
       - "generate_docs" if conversation is complete
       - "continue_conversation" if we need more answers
    """
    if state.get("conversation_complete"):
        return "generate_docs"
    return "continue_conversation"

