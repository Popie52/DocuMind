import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

SYSTEM_PROMPT = """
You are a helpful document assistant.

Rules:
- Answer ONLY using the provided context.
- If the answer is not in the context, say:
  "I could not find this in the document."
- Do not guess or add external information.
- Be concise and accurate.
"""

def generate_answer(context: str, question: str):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Context:
{context}

Question:
{question}
""")
    ]

    response = model.invoke(messages)
    return response.content