from typing import Tuple, Optional


def validate_user_input(text: str) -> Tuple[bool, Optional[str]]:
    if not text or not text.strip():
        return False, "Please enter a meaningful query."
    if len(text.strip()) < 10:
        return False, "Make the description a bit more detailed (minimum 10 characters)."
    return True, None

