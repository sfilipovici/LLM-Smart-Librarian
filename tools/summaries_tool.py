import json
import os


def _load_book_map(path: str = None):
    if path is None:
        # Use the directory of this file to build the default path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(script_dir, "..", "data", "book_summaries.json")
        default_path = os.path.normpath(default_path)
        path = os.environ.get("BOOKS_PATH", default_path)
    data = json.load(open(path, "r", encoding="utf-8"))
    return {b["title"]: b["summary_full"] for b in data}

BOOKS = _load_book_map()

def get_summary_by_title(title: str) -> str:
    return BOOKS.get(title, "Summary not found. Verifică dacă titlul este exact.")

# OpenAI tool schema for function calling
tools = [{
    "type": "function",
    "function": {
        "name": "get_summary_by_title",
        "description": "Returnează rezumatul complet pentru un titlu exact de carte.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Titlul exact al cărții"}
            },
            "required": ["title"]
        }
    }
}]
