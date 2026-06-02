from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_chunks(
    question: str,
    chunks: list,
    top_k: int = 3,
):
    if not chunks:
        return []
    pairs = [
        (question, chunk["text"])
        for chunk in chunks
    ]

    scores = model.predict(
        pairs
    )

    ranked = []

    for chunk, score in zip(
        chunks,
        scores,
    ):
        chunk = dict(chunk)
        chunk["rerank_score"] = (
            float(score)
        )
        ranked.append(chunk)

    ranked.sort(
        key=lambda x:
        x["rerank_score"],
        reverse=True,
    )

    return ranked[:top_k]