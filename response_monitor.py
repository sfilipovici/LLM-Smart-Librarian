import json
from datetime import datetime

def record_response(session_id, prompt, response_obj):
    """
    Append a JSONL log entry with timestamp, model, usage and content.
    Usage:
      record_response(None, user_prompt, openai_response_object)
    """
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "prompt": prompt,
    }
    try:
        entry["model"] = getattr(response_obj, "model", None)
        usage = getattr(response_obj, "usage", None)
        if usage:
            entry["usage"] = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }
        # best-effort to capture text
        try:
            entry["content"] = response_obj.choices[0].message.content
        except Exception:
            entry["content"] = None
    except Exception:
        pass

    with open("response_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
