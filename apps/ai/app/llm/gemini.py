import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

SYSTEM_PROMPT = """
You are a retrieval-augmented AI assistant.

Answer questions using ONLY the provided document context.

Rules:
- Do NOT use external knowledge.
- Do NOT guess or fabricate information.
- If the answer is not found in the context,
  respond exactly:
  "I could not find this in the document."

Answer Guidelines:
- Be concise, accurate, and factual.
- Provide a complete explanation based on the context.
- Use multiple relevant facts from the context.
- Use bullet points when helpful.
- Base every factual statement on the context.
- If the context is ambiguous or conflicting,
  mention that clearly.
"""

def generate_answer(context: str, question: str):

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),

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
    ]

    response = model.invoke(messages)

    return response.content