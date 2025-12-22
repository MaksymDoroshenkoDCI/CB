from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, Optional, List
from .agents import outline_agent, drafting_agent, refinement_agent
from .conversation_agent import conversation_agent, all_answers_collected
from .memory import load_memory, save_memory
from .storage import save_doc_txt


class DocStateDict(TypedDict, total=False):
    user_input: str
    project_name: Optional[str]
    system_context: Optional[str]
    doc_outline: Optional[str]
    draft_doc: Optional[str]
    refined_doc: Optional[str]
    history: List[Dict[str, Any]]
    session_id: Optional[str]
    # Fields for conversational agent
    answers: Optional[Dict[str, str]]
    current_question: Optional[int]
    current_question_text: Optional[str]
    conversation_complete: Optional[bool]
    collected_requirements: Optional[str]


def persist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_doc = state.get("refined_doc") or state.get("draft_doc") or ""
    path = save_doc_txt(final_doc, session_id=state.get("session_id") or "default")

    history = load_memory()
    history.append(
        {
            "session_id": state.get("session_id"),
            "user_input": state.get("user_input"),
            "outline": state.get("doc_outline"),
            "doc_path": path,
        }
    )
    save_memory(history)

    if "history" not in state:
        state["history"] = []
    state["history"].append({"role": "system", "content": f"Document saved to {path}"})
    return state


def build_graph(use_conversation: bool = True):
    """
    Builds LangGraph workflow.
    
    Args:
        use_conversation: If True, adds conversational agent as entry point.
                         If False, uses old workflow without dialog.
    """
    graph = StateGraph(DocStateDict)

    # Add conversational agent
    if use_conversation:
        graph.add_node("conversation_agent", conversation_agent)
        graph.set_entry_point("conversation_agent")
        
        # Conditional transition: continue dialog or proceed to generation
        graph.add_conditional_edges(
            "conversation_agent",
            all_answers_collected,
            {
                "continue_conversation": "conversation_agent",  # Return to dialog
                "generate_docs": "outline_agent"  # Proceed to generation
            }
        )
    else:
        graph.set_entry_point("outline_agent")

    # Add standard agents
    graph.add_node("outline_agent", outline_agent)
    graph.add_node("drafting_agent", drafting_agent)
    graph.add_node("refinement_agent", refinement_agent)
    graph.add_node("persist_node", persist_node)

    # Standard generation pipeline
    graph.add_edge("outline_agent", "drafting_agent")
    graph.add_edge("drafting_agent", "refinement_agent")
    graph.add_edge("refinement_agent", "persist_node")
    graph.add_edge("persist_node", END)

    return graph.compile()


# Standard workflow with conversational agent
workflow = build_graph(use_conversation=True)

# Workflow without dialog (for backward compatibility)
workflow_direct = build_graph(use_conversation=False)

