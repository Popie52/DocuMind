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

from app.observability.metrics import (
    increment,
    add_response_time,
)


async def ask_question(
    question: str,
):
    timer = Timer()
    increment(
        "questions_total"
    )
    response = graph.invoke(
        {
            "question": question,
        }
    )

    logger.info(
        f"Total request time "
        f"{timer.elapsed_ms()} ms"
    )

    add_response_time(timer.elapsed_ms())

    citations = (
        format_citations(response["chunks"])
    )

    return {
        "answer": response["answer"],
        "citations": citations,
    }
