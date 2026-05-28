from app.retrievers.qdrant import retrieve_chunks

from app.llm.gemini import generate_answer


def retrieve_node(state):
    print("Running retrieve node")
    question = state["question"]
    chunks = retrieve_chunks(question)

    context = "\n\n".join(
        chunk["text"]
        if isinstance(chunk, dict)
        else chunk
        for chunk in chunks
    )

    return {
        "chunks": chunks,
        "context": context,
    }

def generate_node(state):
    print("Running generate node")
    answer = generate_answer(
        context=state["context"],
        question=state["question"],
    )
    return {
        "answer": answer,
    }

