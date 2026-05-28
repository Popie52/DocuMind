from typing import TypedDict

class RAGState(TypedDict):
    question: str
    chunks: str
    context: str
    answer: str
