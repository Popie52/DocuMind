import os
import time
from uuid import uuid4
import aiofiles

from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Form,
    Request,
    HTTPException
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
    request: Request,
    document_id: Annotated[str, Form(...)],
    session_id: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
):
    req_id = request.headers.get("x-request-id", str(uuid4()))
    start_time = time.time()
    
    print(f"[AI] [{req_id}] /parse started")
    print(f"[AI] [{req_id}] Session id: {session_id}, Document id: {document_id}")
    
    try:
        file_path = f"{UPLOAD_DIR}/{uuid4()}-{file.filename}"

        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                await buffer.write(chunk)
                
        file_size = os.path.getsize(file_path)
        print(f"[AI] [{req_id}] File written. Size: {file_size} bytes")

        print(f"[AI] [{req_id}] Parsing document")
        parse_start = time.time()
        parsed_pages = await parse_document(file_path)
        print(f"[AI] [{req_id}] Parsing completed. Found {len(parsed_pages) if parsed_pages else 0} pages. Took {time.time() - parse_start:.2f}s")

        if not parsed_pages:
            raise ValueError("PDF parsing failed")

        print(f"[AI] [{req_id}] Ingestion started")
        ingest_start = time.time()
        chunks_created = await ingest_document(
            pages=parsed_pages,
            document_id=document_id,
            session_id=session_id,
            filename=file.filename,
        )
        print(f"[AI] [{req_id}] Ingestion completed. {chunks_created} chunks. Took {time.time() - ingest_start:.2f}s")

        print(f"[AI] [{req_id}] Request completed successfully. Time taken: {time.time() - start_time:.2f}s")
        return {
            "filename": file.filename,
            "chunks": chunks_created,
            "session_id": session_id,
        }
        
    except Exception as e:
        print(f"[AI] [{req_id}] Request failed: {str(e)}")
        # Raise HTTPException so FastAPI catches it and returns 500 cleanly
        raise HTTPException(status_code=500, detail=str(e))
