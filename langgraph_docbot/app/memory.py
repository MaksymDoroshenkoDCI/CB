import json
import os
from typing import List, Dict
from .config import settings


def load_memory() -> List[Dict]:
    directory = os.path.dirname(settings.MEMORY_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    if not os.path.exists(settings.MEMORY_FILE):
        return []

    with open(settings.MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_memory(history: List[Dict]):
    directory = os.path.dirname(settings.MEMORY_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(settings.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

