from sentence_transformers import (
    SentenceTransformer,
)
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

def embed_text(text: str):
    embedding = model.encode(text)
    return embedding.tolist()