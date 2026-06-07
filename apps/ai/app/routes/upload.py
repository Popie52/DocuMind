import os
from uuid import uuid4
import aiofiles

from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Form,
)

from app.services.parser import parse_document
from app.services.ingest import ingest_document

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


@router.post("/parse")
async def parse_pdf(
    document_id: Annotated[
        str,
        Form(...),
    ],
    session_id: Annotated[
        str,
        Form(...),
    ],
    file: Annotated[
        UploadFile,
        File(...),
    ],
):
    file_path = (
        f"{UPLOAD_DIR}/"
        f"{uuid4()}-{file.filename}"
    )

    async with aiofiles.open(
        file_path,
        "wb",
    ) as buffer:
        while chunk := await file.read(
            1024 * 1024
        ):
            await buffer.write(chunk)

    parsed_pages = await parse_document(
        file_path
    )

    if not parsed_pages:
        raise ValueError(
            "PDF parsing failed"
        )

    chunks_created = await ingest_document(
        pages=parsed_pages,
        document_id=document_id,
        session_id=session_id,
        filename=file.filename,
    )

    return {
        "filename": file.filename,
        "chunks": chunks_created,
        "session_id": session_id,
    }
