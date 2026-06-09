from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

REWRITE_PROMPT = """
You are a query rewriting engine.

Your task is to convert conversational
follow-up questions into standalone questions.

Rules:

- Never answer.
- Never summarize.
- Never add information.
- Preserve meaning.
- Use conversation history when necessary.
- If already standalone,
  return the original question.
- Return ONLY the rewritten query.
"""

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

def rewrite_query(
    question: str,
    history: list | None = None,
) -> str:
    history = history or []

    messages = [
        SystemMessage(
            content=REWRITE_PROMPT
        )
    ]

    for msg in history[-6:]:
        if msg.role == "user":
            messages.append(
                HumanMessage(
                    content=msg.content
                )
            )
        elif msg.role in ["assistant", "ai"]:
            messages.append(
                AIMessage(
                    content=msg.content
                )
            )

    messages.append(
        HumanMessage(
            content=question
        )
    )

    response = model.invoke(
        messages
    )

    return response.content.strip()
