"""
Documentation Generation Agent
Generates complete technical documentation directly from collected requirements.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
from .config import settings
from .storage import save_doc_txt


def get_llm():
    """Returns configured LLM for documentation generation."""
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,  # Default: gemini-2.5-flash
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )


DOCUMENTATION_GENERATION_PROMPT = """You are an experienced technical documentation writer for IT systems.

IMPORTANT: The collected requirements below may contain answers in ANY language (English, Ukrainian, Russian, or any other language). 
You must understand and process all requirements regardless of the language they are written in.
The final documentation MUST be written in English only.

{project_context}

COLLECTED REQUIREMENTS:
{collected_requirements}

Create complete technical documentation that includes:

1. **Introduction and Overview**
   - System purpose and main goals
   - Target audience
   - Key features summary

2. **System Architecture**
   - Overall architecture description
   - Main components and modules
   - System diagrams (describe in text format)
   - Data flow

3. **Technology Stack**
   - Programming languages
   - Frameworks and libraries
   - Databases and data storage
   - Development tools
   - Deployment tools

4. **Functionality**
   - Detailed feature descriptions
   - Use cases
   - User workflows
   - Business logic

5. **API and Integrations**
   - API endpoints (if applicable)
   - External service integrations
   - Third-party APIs
   - Data exchange formats

6. **Database Design**
   - Database schema
   - Data models
   - Relationships
   - Indexes and constraints

7. **Security**
   - Authentication mechanisms
   - Authorization rules
   - Data protection
   - Security best practices

8. **Deployment and Infrastructure**
   - Deployment process
   - Infrastructure requirements
   - CI/CD pipeline
   - Environment configuration

9. **Testing**
   - Testing strategy
   - Test types
   - Testing tools

10. **Monitoring and Logging**
    - Monitoring approach
    - Logging strategy
    - Error handling

11. **Developer Guide**
    - Getting started
    - Development setup
    - Contribution guidelines

Requirements for documentation:
- IMPORTANT: Write ONLY in English, regardless of the language of the input requirements
- Understand and interpret requirements in any language (Ukrainian, Russian, English, etc.)
- Translate and process all information from the collected requirements into English
- Write in clear, professional English
- Use proper technical terminology
- Include code examples where relevant
- Add configuration examples
- Be comprehensive and detailed
- Structure with clear headings and sections
- Use markdown formatting

Generate the complete documentation now in English:"""


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
    prompt = DOCUMENTATION_GENERATION_PROMPT.format(
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
