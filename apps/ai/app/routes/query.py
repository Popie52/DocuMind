from app.retrievers.qdrant import retrieve_chunks
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag import (
    ask_question,
)

router = APIRouter()

class QueryRequest(
    BaseModel
):
    question: str


@router.post("/query")
async def query_documents(body: QueryRequest):
    response = (
        await ask_question(
            body.question,
        )
    )

    return response