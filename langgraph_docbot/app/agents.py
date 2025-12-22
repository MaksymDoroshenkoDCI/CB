from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
from .config import settings
from .prompts import DOC_OUTLINE_PROMPT, DOC_DRAFT_PROMPT, DOC_REFINEMENT_PROMPT


def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def outline_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()
    project_context = ""
    if state.get("project_name"):
        project_context = f"Project: {state['project_name']}\n\n"
    
    # Use collected requirements from dialog if available
    user_input = state.get("collected_requirements") or state.get("user_input", "")
    
    prompt = DOC_OUTLINE_PROMPT.format(
        project_context=project_context,
        user_input=user_input
    )
    resp = llm.invoke(prompt)
    state["doc_outline"] = resp.content
    if "history" not in state:
        state["history"] = []
    state["history"].append({"role": "agent_outline", "content": state["doc_outline"]})
    return state


def drafting_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()
    project_context = ""
    if state.get("project_name"):
        project_context = f"Project: {state['project_name']}\n\n"
    
    # Use collected requirements from dialog if available
    user_input = state.get("collected_requirements") or state.get("user_input", "")
    
    prompt = DOC_DRAFT_PROMPT.format(
        project_context=project_context,
        outline=state.get("doc_outline", ""),
        user_input=user_input,
    )
    resp = llm.invoke(prompt)
    state["draft_doc"] = resp.content
    if "history" not in state:
        state["history"] = []
    state["history"].append({"role": "agent_draft", "content": state["draft_doc"]})
    return state


def refinement_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()
    prompt = DOC_REFINEMENT_PROMPT.format(draft=state.get("draft_doc", ""))
    resp = llm.invoke(prompt)
    state["refined_doc"] = resp.content
    if "history" not in state:
        state["history"] = []
    state["history"].append({"role": "agent_refine", "content": state["refined_doc"]})
    return state

