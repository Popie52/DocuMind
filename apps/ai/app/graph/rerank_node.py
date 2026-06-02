from app.rerankers.cross_encoder import (
    rerank_chunks,
)


def rerank_node(state):
    chunks = state["chunks"]

    if not chunks:
        return {
            "chunks": [],
            "context": "",
        }

    reranked = rerank_chunks(
        question=state["question"],
        chunks=chunks,
        top_k=3,
    )

    context_parts = []

    for chunk in reranked:
        context_parts.append(
            f"""
SOURCE:
{chunk["filename"]}

CHUNK:
{chunk["chunk_index"]}

CONTENT:
{chunk["text"]}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    return {
        "chunks": reranked,
        "context": context,
    }
