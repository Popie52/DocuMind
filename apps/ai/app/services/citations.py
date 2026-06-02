def format_citations(chunks):
    citations = []

    for chunk in chunks:
        citations.append({
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "chunk": chunk["chunk_index"],
        })

    return citations
