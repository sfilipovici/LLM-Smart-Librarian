import sys
import os
from dotenv import load_dotenv

load_dotenv()  # <-- Move this to the top, before other imports

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from openai import OpenAI

from rag.retriever import retrieve
from tools.summaries_tool import get_summary_by_title, tools as summaries_tools
from response_monitor import record_response

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "Ești un asistent bibliotecar. Folosește contextul RAG pentru a recomanda O SINGURĂ carte "
    "potrivită cererii utilizatorului. După ce alegi titlul, emite un apel de funcție "
    "`get_summary_by_title` cu titlul exact. Ton: concis, prietenos."
)

def run_turn(client, user_input: str) -> str:
    # 1) Retrieve top-k passages
    retrieved = retrieve(user_input, k=5)
    if retrieved:
        context_lines = [
            f"- {hit['metadata']['title']}: {hit['document']} (teme: {', '.join(hit['metadata']['themes'])})"
            for hit in retrieved
        ]
        context_text = "Context (RAG):\n" + "\n".join(context_lines)
    else:
        context_text = "Context (RAG): none"

    # 2) Ask the model for a recommendation; allow it to call the summary tool
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
            {"role": "system", "content": context_text},
        ],
        tools=summaries_tools,
        tool_choice="auto"
    )
    message = response.choices[0].message

    # 3) If the model called our function, run it and do a final pass
    if getattr(message, "tool_calls", None):
        tool_messages = []
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_summary_by_title":
                args = json.loads(tool_call.function.arguments)
                result = get_summary_by_title(args["title"])
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        # Now do the final pass, including all tool messages
        final = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
                {"role": "system", "content": context_text},
                message,
                *tool_messages
            ],
            tools=summaries_tools,
            tool_choice="none"
        )
        record_response(final.model_dump(), user_input, response.model_dump())
        return final.choices[0].message.content

    # 4) No tool call; just log and return the assistant's message
    record_response(None, user_input, response.model_dump())
    return message.content

def chat_loop():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("📚 Smart Librarian (CLI). Scrie 'exit' pentru a ieși.")
    while True:
        user_input = input("Tu: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("👋 La revedere!")
            break
        try:
            answer = run_turn(client, user_input)
            print("Asistent:", answer, "\n")
        except Exception as e:
            print("⚠️ Eroare:", e, "\n")

if __name__ == "__main__":
    chat_loop()
