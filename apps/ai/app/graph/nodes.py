from app.retrievers.qdrant import retrieve_chunks

from app.llm.gemini import generate_answer


def retrieve_node(state):
    print("Running retrieve node")
    question = state["question"]
    chunks = retrieve_chunks(question)

    print("\n=== RETRIEVAL ===")
    if not chunks:
        return {
            "chunks": [],
        }

    for chunk in chunks:
        print(
            chunk["score"],
            chunk["filename"],
            chunk["chunk_index"],
        )

    return {
        "chunks": chunks,
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
