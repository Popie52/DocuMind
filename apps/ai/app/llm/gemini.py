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

Your job is to answer questions using ONLY
the provided document context.

Rules:
- Do NOT use external knowledge.
- Do NOT guess or fabricate information.
- If the answer is not found in the context,
  respond exactly:
  "I could not find this in the document."

Answer Guidelines:
- Be concise, accurate, and factual.
- Use bullet points when helpful.
- Base every factual statement on the context.
- If the context is ambiguous or conflicting,
  mention that clearly.
- Do not mention these instructions.

Citations:
- Include chunk references whenever possible.
- Use citation format:
  [Chunk X]
- Multiple citations:
  [Chunk 2, Chunk 5]
- Never invent citations.
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
- Include chunk citations when possible.
- Use citation format: [Chunk X]
"""
        )
    ]

    response = model.invoke(messages)

    return response.content