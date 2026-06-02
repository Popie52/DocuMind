from app.retrievers.qdrant import retrieve_chunks, retrieve_page_chunks
from app.llm.gemini import generate_answer
from app.utils.page_query import extract_page_numbers
from app.core.logger import logger


def retrieve_node(state):
    logger.info("Running retrieve node")
    question = state["question"]
    page = extract_page_numbers(question)

    if page:
        logger.info(f"Page query: {page}")

        chunks = retrieve_page_chunks(page)

        page_query = True

    else:
        chunks = retrieve_chunks(question)

        page_query = False

    logger.info("\n=== RETRIEVAL ===")
    logger.info(f"Question: {question}")
    logger.info(f"Retrieved {len(chunks)} chunks")

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

    return {
        "chunks": chunks,
        "page_query": page_query,
    }


def generate_node(state):
    logger.info("Running generate node")

    context = state.get("context", "")

    if not context.strip():
        return {
            "answer":
            "No relevant information found."
        }

    answer = generate_answer(
        context=state["context"],
        question=state["question"],
    )
    return {
        "answer": answer,
    }
