import streamlit as st
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from openai import OpenAI
from rag.retriever import retrieve
from tools.summaries_tool import get_summary_by_title, tools as summaries_tools

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = (
    "Ești un asistent bibliotecar. Folosește contextul RAG pentru a recomanda O SINGURĂ carte "
    "potrivită cererii utilizatorului. După ce alegi titlul, emite un apel de funcție "
    "`get_summary_by_title` cu titlul exact. Ton: concis, prietenos."
)

def run_turn(client, user_input: str) -> str:
    # Build conversation history for OpenAI, interleaving RAG context after each user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = st.session_state.history.copy()
    history.append(("Tu", user_input))  # Add the current user input to the history

    for idx, (speaker, text) in enumerate(history):
        if speaker == "Tu":
            messages.append({"role": "user", "content": text})
            # Add RAG context after each user message
            retrieved = retrieve(text, k=5)
            if retrieved:
                context_lines = [
                    f"- {hit['metadata']['title']}: {hit['document']} (teme: {', '.join(hit['metadata']['themes'])})"
                    for hit in retrieved
                ]
                context_text = "Context (RAG):\n" + "\n".join(context_lines)
                messages.append({"role": "system", "content": context_text})
            else:
                messages.append({"role": "system", "content": "Context (RAG): none"})
        elif speaker == "Asistent":
            messages.append({"role": "assistant", "content": text})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=summaries_tools,
        tool_choice="auto"
    )
    message = response.choices[0].message

    if getattr(message, "tool_calls", None):
        tool_messages = []
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_summary_by_title":
                import json
                args = json.loads(tool_call.function.arguments)
                result = get_summary_by_title(args["title"])
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        final = client.chat.completions.create(
            model=MODEL,
            messages=messages + [message, *tool_messages],
            tools=summaries_tools,
            tool_choice="none"
        )
        return final.choices[0].message.content
    return message.content

# --- Streamlit UI ---
st.set_page_config(page_title="Smart Librarian", page_icon="📚")

# Custom CSS for chat bubbles and layout
st.markdown("""
<style>
.chat-container {
    max-width: 700px;
    margin: 0 auto;
    padding-bottom: 80px;
}
.bubble-user {
    background: #2563eb;
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px auto;
    max-width: 70%;
    text-align: right;
    word-break: break-word;
    box-shadow: 0 2px 8px #0001;
    align-self: flex-end;
}
.bubble-assistant {
    background: #f0f2f6;
    color: #222;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px auto 8px 0;
    max-width: 70%;
    text-align: left;
    word-break: break-word;
    box-shadow: 0 2px 8px #0001;
    align-self: flex-start;
}
.bubble-error {
    background: #fee;
    color: #a00;
    padding: 12px 18px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 70%;
    word-break: break-word;
    border: 1px solid #faa;
}
.stTextInput > div > div > input {
    font-size: 1.1rem;
}
.input-row {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    background: white;
    padding: 16px 0 8px 0;
    box-shadow: 0 -2px 8px #0001;
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Smart Librarian")

if "history" not in st.session_state:
    st.session_state.history = []

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chat history display
st.markdown('<div class="chat-container" style="display:flex;flex-direction:column;">', unsafe_allow_html=True)
for speaker, text in st.session_state.history:
    if speaker == "Tu":
        st.markdown(f"<div class='bubble-user'>{text}</div>", unsafe_allow_html=True)
    elif speaker == "Asistent":
        st.markdown(f"<div class='bubble-assistant'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-error'>{text}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input at the bottom, always visible
with st.form("chat_form", clear_on_submit=True):
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    user_input = st.text_input(
        "Mesaj", "", placeholder="Scrie întrebarea ta…", label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Trimite")
    st.markdown('</div>', unsafe_allow_html=True)
    if submitted and user_input.strip():
        try:
            answer = run_turn(client, user_input)
            st.session_state.history.append(("Tu", user_input))
            st.session_state.history.append(("Asistent", answer))
            st.rerun()
        except Exception as e:
            st.session_state.history.append(("Eroare", str(e)))
            st.rerun()