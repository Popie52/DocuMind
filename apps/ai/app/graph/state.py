from typing import TypedDict, List, Dict, Any, NotRequired


class Chunk(TypedDict):
    text: str
    score: float
    rerank_score: NotRequired[float]
    filename: str
    document_id: str | None
    chunk_index: int


class RAGState(TypedDict):
    question: str
    chunks: List[Chunk]
    context: str
    answer: str