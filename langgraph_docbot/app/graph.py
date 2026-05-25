"""
LangGraph workflow for generating project documentation:
Conversation Agent -> Documentation Agent -> Save -> END
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, Optional, List
from .agents import documentation_agent
from .conversation_agent import conversation_agent, all_answers_collected
from .memory import load_memory, save_memory


class DocStateDict(TypedDict, total=False):
    user_input: str
    project_name: Optional[str]
    system_context: Optional[str]
    history: List[Dict[str, Any]]
    session_id: Optional[str]
    # Fields for conversational agent
    answers: Optional[Dict[str, str]]
    current_question: Optional[int]
    current_question_text: Optional[str]
    current_question_id: Optional[int]
    current_question_category: Optional[str]
    questions_data: Optional[List[Dict[str, Any]]]
    conversation_complete: Optional[bool]
    collected_requirements: Optional[str]
    # Fields for documentation
    documentation: Optional[str]
    doc_path: Optional[str]
    error: Optional[str]


def save_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Saves documentation to memory/history."""
    doc_path = state.get("doc_path")
    documentation = state.get("documentation", "")
    
    if doc_path and documentation:
        history = load_memory()
        history.append(
            {
                "session_id": state.get("session_id"),
                "user_input": state.get("user_input"),
                "collected_requirements": state.get("collected_requirements"),
                "doc_path": doc_path,
            }
        )
        save_memory(history)
        
        if "history" not in state:
            state["history"] = []
        state["history"].append({
            "role": "system",
            "content": f"Documentation saved to {doc_path}"
        })
    
    return state


def build_graph():
    """
    Builds simplified LangGraph workflow:
    Conversation Agent -> Documentation Agent -> Save -> END
    """
    graph = StateGraph(DocStateDict)

    # Add conversational agent (entry point)
    graph.add_node("conversation_agent", conversation_agent)
    graph.set_entry_point("conversation_agent")
    
    # Conditional transition: continue dialog or proceed to generation
    graph.add_conditional_edges(
        "conversation_agent",
        all_answers_collected,
        {
            "continue_conversation": END,  # Stop and wait for user input via API
            "generate_docs": "documentation_agent"  # Proceed to documentation generation
        }
    )
    
    # Add documentation generation agent
    graph.add_node("documentation_agent", documentation_agent)
    
    # Add save node
    graph.add_node("save_node", save_node)
    
    # Simple pipeline: documentation -> save -> END
    graph.add_edge("documentation_agent", "save_node")
    graph.add_edge("save_node", END)

    return graph.compile()


# Main workflow
workflow = build_graph()
