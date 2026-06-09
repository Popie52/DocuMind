from app.services.citations import format_citations

from app.graph.workflow import graph
from app.core.timer import Timer
from app.core.logger import logger

from app.observability.metrics import (
    increment,
    add_response_time,
)


def ask_question(
    question: str,
    session_id: str,
    history: list,
):
    timer = Timer()

    increment("questions_total")

    response = graph.invoke(
        {
            "question": question,
            "session_id": session_id,
            "history": history,
        }
    )

    logger.info(
        f"Total request time "
        f"{timer.elapsed_ms()} ms"
    )

    add_response_time(
        timer.elapsed_ms()
    )

    retrieval_ms = response.get("retrieval_ms", 0.0)
    rerank_ms = response.get("rerank_ms", 0.0)
    llm_ms = response.get("llm_ms", 0.0)
    total_ms = retrieval_ms + rerank_ms + llm_ms
    chunks_retrieved = len(response.get("chunks", []))

    print("\n========== QUERY ==========")
    print(f"Question: {question}")
    print(f"Chunks Retrieved: {chunks_retrieved}")
    print(f"Retrieval: {retrieval_ms:.2f} ms")
    print(f"Rerank: {rerank_ms:.2f} ms")
    print(f"LLM: {llm_ms:.2f} ms")
    print(f"Total: {total_ms:.2f} ms")
    print("==========================\n")

    citations = format_citations(
        response["chunks"]
    )

    return {
        "answer": response["answer"],
        "citations": citations,
    }
