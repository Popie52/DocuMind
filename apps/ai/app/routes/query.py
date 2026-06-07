from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag import (
    ask_question,
)

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str


@router.post("/query")
async def query_documents(
    body: QueryRequest,
):
    response = await ask_question(
        question=body.question,
        session_id=body.session_id,
    )

    return response
