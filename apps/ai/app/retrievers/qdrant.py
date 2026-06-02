from app.embeddings.huggingface import (
    embed_text,
)

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
    limit: int = 5,
    min_score: float = 0.65,
    document_id: str | None = None,
):
    query_embedding = (
        embed_text(query)
    )

    search_filter = None

    if document_id:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id
                    ),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        limit=limit,
        query=query_embedding,
        query_filter=search_filter,
    )

    print(type(results))
    # print(results)
    results = results.points

    formatted_results = []

    for result in results:
        print(result.score)
        if result.score < min_score:
            continue

        formatted_results.append({
            "text":
                result.payload["text"],
            "score":
                round(
                    result.score,
                    3,
                ),
            "filename":
                result.payload[
                    "filename"
                ],
            "document_id": result.payload["document_id"],
            "chunk_index":
                result.payload[
                    "chunk_index"
                ],
        })

    return formatted_results
