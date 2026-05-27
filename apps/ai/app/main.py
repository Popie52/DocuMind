from fastapi import FastAPI
from app.routes.upload import (
    router as upload_router
)
from app.vectorstores.qdrant import (
    create_collection,
)

create_collection()

app = FastAPI()

app.include_router(
    upload_router
)

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }