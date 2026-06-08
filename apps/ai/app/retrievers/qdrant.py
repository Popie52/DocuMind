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
    print(f"\n[DEBUG-QUERY] Starting retrieve_chunks")
    print(f"[DEBUG-QUERY] Query: '{query}'")
    print(f"[DEBUG-QUERY] Expected filters -> session_id: {session_id}, document_id: {document_id}")
    
    query_embedding = embed_text(query)
    print(f"[DEBUG-QUERY] Query embedding generated. Dimension: {len(query_embedding)}")

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
    print(f"[DEBUG-QUERY] Search filter structure: {search_filter}")

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=search_filter,
        limit=limit * 3,
    )
    
    print(f"[DEBUG-QUERY] Qdrant returned {len(results.points)} raw points.")

    formatted_results = []

    for result in results.points:
        print(f"[DEBUG-QUERY] Evaluated point score: {result.score:.4f} (Threshold: {min_score})")
        if result.score < min_score:
            print(f"[DEBUG-QUERY] -> Dropping chunk due to low score.")
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

    print(f"[DEBUG-QUERY] Returning {len(formatted_results)} filtered chunks above min_score.")
    return formatted_results


def retrieve_page_chunks(
    pages: list[int],
    session_id: str,
    document_id: str | None = None,
):
    print(f"\n[DEBUG-QUERY] Starting retrieve_page_chunks for pages: {pages}")
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
    print(f"[DEBUG-QUERY] Search filter structure: {search_filter}")

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=search_filter,
        limit=2000,
    )

    points = results[0]
    print(f"[DEBUG-QUERY] Qdrant returned {len(points)} raw points from scroll.")

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

    print(f"[DEBUG-QUERY] Returning {len(chunks)} chunks.")
    return chunks
