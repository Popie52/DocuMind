from app.embeddings.huggingface import (
    embed_text,
)

from app.vectorstores.qdrant import (
    client,
    COLLECTION_NAME,
)


def retrieve_chunks(
    query: str,
    limit: int = 5,
):
    query_embedding = (
        embed_text(query)
    )

    results = client.query_points(
        collection_name=
        COLLECTION_NAME,
        limit=limit,
        query=query_embedding,
    )

    return [
        {
            "score": result.score,
            "text": result.payload["text"]
        }
        for result in results.points
    ]