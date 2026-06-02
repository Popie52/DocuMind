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
    page = extract_page_numbers(question)

    if page:
        logger.info(f"Page query: {page}")
        increment("page_queries_total")

        chunks = retrieve_page_chunks(page)

        page_query = True

    else:
        increment("semantic_queries_total")
        chunks = retrieve_chunks(question)

        page_query = False

    # logger.info("\n=== RETRIEVAL ===")
    logger.info(f"Question: {question}")
    logger.info(f"Retrieved {len(chunks)} chunks")

    time_elapsed = timer.elapsed_ms()
    add_response_time(time_elapsed)

    if not chunks:
        return {
            "chunks": [],
            "page_query": page_query,
        }
    

    for chunk in chunks:
        logger.info(f"""
            page={chunk["page"]}
            score={chunk.get("score", "N/A")}
            file={chunk["filename"]}"""
        )

    logger.info(
        f"Retrived node completed int "
        f"{time_elapsed} ms")
        
    return {
        "chunks": chunks,
        "page_query": page_query,
    }


def generate_node(state):
    logger.info("Running generate node")
    timer = Timer()

    context = state.get("context", "")

    if not context.strip():
        increment(
            "failed_queries_total"
        )
        return {
            "answer":
            "No relevant information found."
        }

    answer = generate_answer(
        context=state["context"],
        question=state["question"],
    )
    logger.info(
        f"Generation completed in "
        f"{timer.elapsed_ms()} ms"
    )
    add_response_time(timer.elapsed_ms())
    return {
        "answer": answer,
    }
