from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
)

from app.chunking.splitter import (
    split_text,
)

from app.embeddings.huggingface import (
    embed_texts
)

from app.vectorstores.qdrant import (
    client,
    COLLECTION_NAME,
)


async def ingest_document(
    pages: list,
    document_id: str,
    filename: str,
):
    all_points = []

    total_chunks = 0

    for page_data in pages:

        page_number = page_data["page"]

        page_text = page_data["text"]

        chunks = split_text(
            page_text
        )

        embeddings = embed_texts(
            chunks
        )

        total_chunks += len(chunks)

        for index, (
            chunk,
            embedding,
        ) in enumerate(
            zip(
                chunks,
                embeddings,
            )
        ):

            all_points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "document_id":
                            document_id,
                        "filename":
                            filename,
                        "chunk_index":
                            index,
                        "page":
                            page_number,
                    },
                )
            )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=all_points,
    )

    return total_chunks
