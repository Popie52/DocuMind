from app.llm.gemini import (
    generate_answer,
)

from app.retrievers.qdrant import (
    retrieve_chunks,
)


async def ask_question(
    question: str,
):
    chunks = retrieve_chunks(
        question
    )

    context = "\n\n".join(
        chunk["text"]
        if isinstance(chunk, dict)
        else chunk
        for chunk in chunks
    )

    try:
        answer = generate_answer(
            context=context,
            question=question,
        )
    except Exception:
        answer = (
            "Failed to generate answer."
        )

    return {
        "answer": answer,
        "chunks": chunks,
    }