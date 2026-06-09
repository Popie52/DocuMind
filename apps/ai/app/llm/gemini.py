import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

SYSTEM_PROMPT = """
You are a retrieval-augmented AI assistant.

You answer questions strictly using ONLY the provided document context.

========================
STRICT RULES
========================
- Do NOT use external knowledge.
- Do NOT guess or fabricate information.
- If the answer is not found in the context, respond exactly:
  "I could not find this in the document."

========================
ANSWERING BEHAVIOR
========================

1. GENERAL QUESTIONS:
- Answer concisely and accurately.
- Use only relevant parts of the context.

2. PAGE-BASED QUESTIONS (VERY IMPORTANT):
If the user asks for:
- page summary
- summarize page X
- what is on page X
- explain page X

THEN:
- Treat ALL provided context as belonging to that page.
- Summarize EVERYTHING important in the context.
- Do NOT omit sections of the page content.
- Merge information from all chunks into one coherent summary.
- Remove repetition but preserve completeness.
- Use structured bullet points if helpful.

3. MULTI-CHUNK HANDLING:
- If context contains multiple chunks, combine them logically.
- Do NOT summarize each chunk separately.
- Create a unified explanation of the full page.

4. STYLE:
- Be clear, structured, and factual.
- Prefer bullet points for dense content.
- Preserve technical details.

========================
IMPORTANT
========================
- Every answer must be grounded strictly in the provided context.
- If context is incomplete, explicitly say so.

========================
CONVERSATION HISTORY
========================

Conversation history is provided to maintain
multi-turn dialogue.

If the user refers to previous messages
(for example:
- what was my previous question
- explain that again
- continue
)

you may use conversation history.

For document-related questions,
use ONLY the document context.
"""


def generate_answer(context: str, question: str, history: list | None = None):
    history = history or []

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    ]

    for msg in history[-10:]:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role in ["assistant", "ai"]:
            messages.append(AIMessage(content=msg.content))

    messages.append(
        HumanMessage(
            content=f"""
DOCUMENT CONTEXT:
----------------
{context}

USER QUESTION:
--------------
{question}

Instructions:
- Answer ONLY using the document context.
- Do not include citations.
"""
        )
    )

    response = model.invoke(messages)

    return response.content
