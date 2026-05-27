from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
)

from app.chunking.splitter import (
    split_text,
)

from app.embeddings.huggingface import (
    embed_text,
)

from app.vectorstores.qdrant import (
    client,
    COLLECTION_NAME,
)


async def ingest_document(
    text: str,
):
    chunks = split_text(text)

    points = []

    for chunk in chunks:
        embedding = embed_text(
            chunk
        )

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text": chunk,
                },
            )
        )

    client.upsert(
        collection_name=
        COLLECTION_NAME,
        points=points,
    )

    return len(chunks)