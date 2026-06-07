from typing import TypedDict, List, NotRequired


class Chunk(TypedDict):
    text: str
    score: float
    rerank_score: NotRequired[float]
    filename: str
    document_id: str | None
    session_id: str
    chunk_index: int
    page: int


class RAGState(TypedDict):
    question: str
    session_id: str
    page_query: bool
    chunks: List[Chunk]
    context: str
    answer: str
    history: list
    retrieval_ms: NotRequired[float]
    rerank_ms: NotRequired[float]
    llm_ms: NotRequired[float]
