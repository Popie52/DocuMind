from app.llm.gemini import (
    generate_answer,
)
from app.services.citations import format_citations

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

    citations = (
        format_citations(response["chunks"])
    )
    
    return {
        "answer": response["answer"],
        "chunks": citations,
    }