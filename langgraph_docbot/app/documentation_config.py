import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .config import settings

def get_documentation_structure_path() -> Path:
    """Returns path to documentation structure JSON file."""
    # Assuming the json file is in the same directory as this file
    return Path(__file__).parent / "documentation_structure.json"

def load_documentation_structure() -> Dict[str, Any]:
    """Loads documentation structure from JSON file."""
    file_path = get_documentation_structure_path()
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def get_chapters() -> List[Dict[str, Any]]:
    """Returns ordered list of chapters."""
    structure = load_documentation_structure()
    chapters = structure.get("chapters", [])
    return sorted(chapters, key=lambda x: x.get("order", 0))

def get_prompt_template() -> Tuple[str, List[str]]:
    """Returns role description and instructions array."""
    structure = load_documentation_structure()
    template = structure.get("prompt_template", {})
    return template.get("role", ""), template.get("instructions", [])

def build_documentation_prompt(project_context: str, collected_requirements: str) -> str:
    """
    Builds complete documentation generation prompt dynamically.
    
    Args:
        project_context: Context string about the project
        collected_requirements: String containing gathered requirements
        
    Returns:
        Formatted prompt string
    """
    role, instructions = get_prompt_template()
    chapters = get_chapters()
    
    # Format instructions as a bulleted list for the prompt if needed, 
    # but based on the original request, it seems we just want to include them naturally.
    # Looking at the original hardcoded prompt, instructions were partially inline/implied.
    # The user request maps "instructions" to specific requirements at the end of the prompt.
    
    formatted_chapters = []
    for chapter in chapters:
        title = chapter.get("title", "")
        order = chapter.get("order", 0)
        subsections = chapter.get("subsections", [])
        
        chapter_str = f"{order}. **{title}**"
        for sub in subsections:
            chapter_str += f"\n   - {sub}"
        
        formatted_chapters.append(chapter_str)
    
    chapters_text = "\n\n".join(formatted_chapters)
    
    # Format requirements for documentation (instructions)
    formatted_instructions = ""
    for instruction in instructions:
        formatted_instructions += f"- {instruction}\n"
        
    # Construct final prompt matching original structure as closely as possible
    prompt = f"""{role}

{project_context}

COLLECTED REQUIREMENTS (from Business Analyst interview):
{collected_requirements}

Create complete technical documentation that includes:

{chapters_text}

Requirements for documentation:
{formatted_instructions}

Generate the complete documentation now in English:"""

    return prompt
