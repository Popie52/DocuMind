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

    if state.get("page_query", False):

        reranked = sorted(
            chunks,
            key=lambda x: (
                x.get("page", 0),
                x.get("chunk_index", 0),
            ),
        )

    else:

        reranked = rerank_chunks(
            question=state["question"],
            chunks=chunks,
            top_k=3,
        )

    pages = {}

    for chunk in reranked:
        page = chunk["page"]

        if page not in pages:
            pages[page] = []

        pages[page].append(
            chunk["text"]
        )

    context_parts = []

    for page in sorted(
        pages.keys()
    ):
        context_parts.append(
            f"\n=== PAGE {page} ===\n"
        )

        context_parts.append(
            "\n\n".join(
                pages[page]
            )
        )

    context = "\n\n".join(
        context_parts
    )

    return {
        "chunks": reranked,
        "context": context,
    }
