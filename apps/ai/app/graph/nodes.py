import time
from app.retrievers.qdrant import retrieve_chunks, retrieve_page_chunks
from app.llm.gemini import generate_answer
from app.utils.page_query import extract_page_numbers
from app.core.logger import logger
from app.core.timer import Timer
from app.observability.metrics import (
    increment,
    add_response_time,
)


def retrieve_node(state):
    logger.info("Running retrieve node")

    timer = Timer()

    question = state["question"]
    session_id = state["session_id"]

    page = extract_page_numbers(question)

    if page:
        logger.info(
            f"Page query: {page}"
        )

        increment(
            "page_queries_total"
        )

        chunks = retrieve_page_chunks(
            pages=page,
            session_id=session_id,
        )

        page_query = True

    else:
        increment(
            "semantic_queries_total"
        )

        chunks = retrieve_chunks(
            query=question,
            session_id=session_id,
        )

        page_query = False

    logger.info(
        f"Question: {question}"
    )

    logger.info(
        f"Session: {session_id}"
    )

    logger.info(
        f"Retrieved {len(chunks)} chunks"
    )

    time_elapsed = timer.elapsed_ms()

    add_response_time(
        time_elapsed
    )

    if not chunks:
        return {
            "chunks": [],
            "page_query": page_query,
        }

    for chunk in chunks:
        logger.info(
            f"""
page={chunk["page"]}
score={chunk.get("score", "N/A")}
file={chunk["filename"]}
"""
        )

    logger.info(
        f"Retrieve node completed in "
        f"{time_elapsed} ms"
    )

    print(f"[RETRIEVAL] {time_elapsed:.2f} ms")
    print(f"Chunks Retrieved: {len(chunks)}")

    return {
        "chunks": chunks,
        "page_query": page_query,
        "retrieval_ms": time_elapsed,
    }


def generate_node(state):
    logger.info("Running generate node")

    context = state.get("context", "")

    if not context.strip():
        increment(
            "failed_queries_total"
        )
        return {
            "answer":
            "No relevant information found."
        }

    history_text = "\n".join(
        [
            f"{m['role']}: {m['content']}"
            for m in state.get("history", [])
        ]
    )

    start = time.perf_counter()
    answer = generate_answer(
        context=state["context"],
        question=state["question"],
        history_text=history_text,
    )
    llm_ms = (time.perf_counter() - start) * 1000

    logger.info(
        f"Generation completed in "
        f"{llm_ms:.2f} ms"
    )
    add_response_time(llm_ms)

    print(f"[LLM] {llm_ms:.2f} ms")

    return {
        "answer": answer,
        "llm_ms": llm_ms,
    }
