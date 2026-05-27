import os
import aiofiles

from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    UploadFile,
)

from app.services.parser import (
    parse_document,
)

from app.services.ingest import (
    ingest_document,
)

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


@router.post("/parse")
async def parse_pdf(file: Annotated[UploadFile, File(...)]):
    file_path = (
        f"{UPLOAD_DIR}/"
        f"{file.filename}"
    )

    async with aiofiles.open(
        file_path,
        "wb",
    ) as buffer:
        while chunk := await file.read(1024 * 1024):
            await buffer.write(chunk)

    parsed_text = await parse_document(
        file_path
    )

    print(parsed_text[:500])

    chunks_created = (
        await ingest_document(parsed_text)
    )

    return {
        "filename": file.filename,
        "chunks": chunks_created,
    }