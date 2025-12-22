import os
import datetime
from typing import Optional
from .config import settings


def save_doc_txt(content: str, session_id: Optional[str] = None) -> str:
    os.makedirs(settings.DOCS_OUTPUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = ["doc"]
    if session_id:
        parts.append(session_id)
    parts.append(ts)
    filename = "_".join(parts) + ".txt"

    path = os.path.join(settings.DOCS_OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

