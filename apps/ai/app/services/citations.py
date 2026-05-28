def format_citations(chunks):
    citations = []

    for chunk in chunks:
        citations.append({
            "filename": chunk["filename"],
            "chunk": chunk["chunk_index"],
        })
        
    return citations