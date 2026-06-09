from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag import (
    ask_question,
)

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    question: str
    session_id: str
    history: list[Message] = []


@router.post("/query")
async def query_documents(
    body: QueryRequest,
):
    response = ask_question(
        question=body.question,
        session_id=body.session_id,
        history=body.history,
    )

    return response
