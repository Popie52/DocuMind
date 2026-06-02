from app.llm.gemini import (
    generate_answer,
)
from app.services.citations import format_citations

from app.retrievers.qdrant import (
    retrieve_chunks,
)

from app.graph.workflow import graph
from app.core.timer import Timer
from app.core.logger import logger


async def ask_question(
    question: str,
):
    timer = Timer()
    response = graph.invoke(
        {
            "question": question,
        }
    )

    logger.info(
        f"Total request time "
        f"{timer.elapsed_ms()} ms"
    )

    citations = (
        format_citations(response["chunks"])
    )

    return {
        "answer": response["answer"],
        "citations": citations,
    }
