from app.embeddings.huggingface import embed_text
from app.vectorstores.qdrant import (
    client,
    COLLECTION_NAME,
)

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)


def retrieve_chunks(
    query: str,
    session_id: str,
    limit: int = 5,
    min_score: float = 0.65,
    document_id: str | None = None,
):
    query_embedding = embed_text(query)

    must_conditions = [
        FieldCondition(
            key="session_id",
            match=MatchValue(
                value=session_id,
            ),
        )
    ]

    if document_id:
        must_conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(
                    value=document_id,
                ),
            )
        )

    search_filter = Filter(
        must=must_conditions,
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=search_filter,
        limit=limit * 3,
    )

    formatted_results = []

    for result in results.points:
        if result.score < min_score:
            continue

        formatted_results.append(
            {
                "text": result.payload["text"],
                "score": round(result.score, 3),
                "filename": result.payload["filename"],
                "document_id": result.payload["document_id"],
                "session_id": result.payload["session_id"],
                "chunk_index": result.payload["chunk_index"],
                "page": result.payload["page"],
            }
        )

    return formatted_results


def retrieve_page_chunks(
    pages: list[int],
    session_id: str,
    document_id: str | None = None,
):
    must_conditions = [
        FieldCondition(
            key="session_id",
            match=MatchValue(
                value=session_id,
            ),
        )
    ]

    if document_id:
        must_conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(
                    value=document_id,
                ),
            )
        )

    page_conditions = [
        FieldCondition(
            key="page",
            match=MatchValue(
                value=page,
            ),
        )
        for page in pages
    ]

    search_filter = Filter(
        must=must_conditions,
        should=page_conditions,
    )

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=search_filter,
        limit=2000,
    )

    points = results[0]

    chunks = []

    for point in points:
        payload = point.payload

        chunks.append(
            {
                "text": payload["text"],
                "filename": payload["filename"],
                "page": payload["page"],
                "document_id": payload["document_id"],
                "session_id": payload["session_id"],
                "chunk_index": payload["chunk_index"],
                "score": 1.0,
            }
        )

    chunks.sort(
        key=lambda x: (
            x["page"],
            x["chunk_index"],
        )
    )

    return chunks
