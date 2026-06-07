from app.rerankers.cross_encoder import (
    rerank_chunks,
)
from app.core.timer import Timer
from app.core.logger import logger
from app.observability.metrics import add_rerank_time
import time


def rerank_node(state):
    logger.info("Running rerank node")
    chunks = state["chunks"]

    if not chunks:
        return {
            "chunks": [],
            "context": "",
            "rerank_ms": 0.0,
        }

    start = time.perf_counter()

    if state.get("page_query", False):

        logger.info(
            f"Page query detected. "
            f"Skipping rerank. "
            f"Chunks={len(chunks)}"
        )

        reranked = sorted(
            chunks,
            key=lambda x: (
                x.get("page", 0),
                x.get("chunk_index", 0),
            ),
        )

    else:

        logger.info(
            f"Running cross-encoder rerank "
            f"on {len(chunks)} chunks"
        )

        reranked = rerank_chunks(
            question=state["question"],
            chunks=chunks,
            top_k=3,
        )

        logger.info(
            f"Reranked -> {len(reranked)} chunks"
        )

    rerank_ms = (time.perf_counter() - start) * 1000
    add_rerank_time(rerank_ms)

    print(f"[RERANK] {rerank_ms:.2f} ms")
    print(f"Chunks After Rerank: {len(reranked)}")

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

    logger.info(
        f"Pages={len(pages)} "
        f"Chunks={len(reranked)} "
        f"ContextChars={len(context)} "
        f"ApproxTokens={len(context.split())}"
    )

    logger.info(
        f"Rerank node completed in "
        f"{rerank_ms:.2f} ms"
    )

    return {
        "chunks": reranked,
        "context": context,
        "rerank_ms": rerank_ms,
    }
