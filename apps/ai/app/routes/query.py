from app.retrievers.qdrant import retrieve_chunks
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(
    BaseModel
):
    question: str


@router.post("/query")
async def query_documents(body: QueryRequest):
    chunks = retrieve_chunks(body.question)

    return {
        "question": body.question,
        "chunks": chunks,
    }