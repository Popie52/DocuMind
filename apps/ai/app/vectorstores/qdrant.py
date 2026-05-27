import os
from dotenv import load_dotenv

from qdrant_client import (
    QdrantClient,
)

from qdrant_client.models import (
    Distance,
    VectorParams,
)

load_dotenv()

COLLECTION_NAME = (
    "documents"
)


client = QdrantClient(
    url=os.getenv(
        "QDRANT_URL"
    )
)


def create_collection():
    collections = (
        client.get_collections()
    )

    exists = any(
        collection.name
        == COLLECTION_NAME
        for collection
        in collections.collections
    )

    if not exists:
        client.create_collection(
            collection_name=
            COLLECTION_NAME,
            vectors_config=
            VectorParams(
                size=384,
                distance=
                Distance.COSINE,
            ),
        )