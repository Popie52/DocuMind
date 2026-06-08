from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
)

from app.chunking.splitter import (
    split_text,
)

from app.embeddings.huggingface import (
    embed_texts,
)

from app.vectorstores.qdrant import (
    client,
    COLLECTION_NAME,
)


async def ingest_document(
    pages: list,
    document_id: str,
    session_id: str,
    filename: str,
):
    print(f"\n[DEBUG-INGEST] Starting ingest_document for {filename}")
    print(f"[DEBUG-INGEST] Session ID: {session_id} | Document ID: {document_id}")
    all_points = []

    total_chunks = 0

    for page_data in pages:
        page_number = page_data["page"]
        page_text = page_data["text"]

        chunks = split_text(page_text)

        if not chunks:
            continue

        print(f"[DEBUG-INGEST] Generating embeddings for {len(chunks)} chunks on page {page_number}")
        embeddings = embed_texts(chunks)
        print(f"[DEBUG-INGEST] Embeddings generated. Count: {len(embeddings)}.")
        if embeddings:
            print(f"[DEBUG-INGEST] Sample vector dimension: {len(embeddings[0])}")

        total_chunks += len(chunks)

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            all_points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "session_id": session_id,
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": index,
                        "page": page_number,
                    },
                )
            )

    print(f"[DEBUG-INGEST] Finished processing chunks. Total points to insert: {len(all_points)}")

    if all_points:
        print(f"[DEBUG-INGEST] Upserting {len(all_points)} points to collection '{COLLECTION_NAME}'...")
        response = client.upsert(
            collection_name=COLLECTION_NAME,
            points=all_points,
        )
        print(f"[DEBUG-INGEST] Qdrant insert success response: {response}")
        
        # Verify collection count
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        print(f"[DEBUG-INGEST] Qdrant total points after insert: {collection_info.points_count}")
    else:
        print("[DEBUG-INGEST] Warning: No points generated to insert.")

    return total_chunks
