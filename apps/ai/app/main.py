from fastapi import FastAPI
from app.routes.upload import (
    router as upload_router
)
from app.vectorstores.qdrant import (
    create_collection,
)
from app.routes.query import (
    router as query_router
)
from app.routes.metrics import (
    router as metrics_router
)

create_collection()

app = FastAPI()

app.include_router(
    upload_router
)

app.include_router(
    query_router
)

app.include_router(
    metrics_router
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
