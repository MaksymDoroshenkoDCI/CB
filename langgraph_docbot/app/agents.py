"""
Documentation Generation Agent
Generates complete technical documentation directly from collected requirements.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
from .config import settings
from .storage import save_doc_txt
from .documentation_config import build_documentation_prompt


def get_llm():
    """Returns configured LLM for documentation generation."""
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,  # Default: gemini-2.5-flash
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def documentation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates complete technical documentation from collected requirements.
    Sends prompt directly to Gemini 2.5 Flash and saves the result.
    """
    llm = get_llm()
    
    # Get project context
    project_context = ""
    if state.get("project_name"):
        project_context = f"Project Name: {state['project_name']}\n\n"
    
    # Get collected requirements
    collected_requirements = state.get("collected_requirements") or state.get("user_input", "")
    
    if not collected_requirements:
        state["documentation"] = "Error: No requirements collected."
        return state
    
    # Format prompt
    prompt = build_documentation_prompt(
        project_context=project_context,
        collected_requirements=collected_requirements
    )
    
    # Generate documentation
    try:
        response = llm.invoke(prompt)

        documentation = response.content
        
        # Save documentation
        state["documentation"] = documentation
        
        # Save to file
        session_id = state.get("session_id") or "default"
        doc_path = save_doc_txt(documentation, session_id=session_id)
        state["doc_path"] = doc_path
        
        # Add to history
        if "history" not in state:
            state["history"] = []
        state["history"].append({
            "role": "system",
            "content": f"Documentation generated and saved to {doc_path}"
        })
        
    except Exception as e:
        error_msg = f"Error generating documentation: {str(e)}"
        state["documentation"] = error_msg
        state["error"] = error_msg
        print(error_msg)
    
    return state
