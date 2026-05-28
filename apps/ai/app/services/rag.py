from app.llm.gemini import (
    generate_answer,
)

from app.retrievers.qdrant import (
    retrieve_chunks,
)

from app.graph.workflow import graph

async def ask_question(
    question: str,
):
    response = graph.invoke(
        {"question": question,}
    )
    
    return {
        "answer": response["answer"],
        "chunks": response["chunks"],
    }