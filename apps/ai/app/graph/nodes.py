from app.retrievers.qdrant import retrieve_chunks, retrieve_page_chunks
from app.llm.gemini import generate_answer
from app.utils.page_query import extract_page_numbers


def retrieve_node(state):
    print("Running retrieve node")
    question = state["question"]
    page = extract_page_numbers(question)

    if page:
        print(f"Page query: {page}")

        chunks = retrieve_page_chunks(page)

        page_query = True

    else:
        chunks = retrieve_chunks(question)

        page_query = False

    print("\n=== RETRIEVAL ===")

    if not chunks:
        return {
            "chunks": [],
            "page_query": page_query,
        }

    for chunk in chunks:
        print(
            chunk.get("score", "N/A"),
            chunk["filename"],
            chunk["chunk_index"],
        )

    return {
        "chunks": chunks,
        "page_query": page_query,
    }


def generate_node(state):
    print("Running generate node")

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
