import os
import asyncio
from pathlib import Path
from llama_parse import LlamaParse
from dotenv import load_dotenv

load_dotenv()

parser = LlamaParse(
    api_key=os.getenv('LLAMA_PARSE_API_KEY'),
    result_type="markdown",
)


async def parse_document(file_path: str):
    print(f"\n[DEBUG-INGEST] Starting parse_document for file: {file_path}")
    documents = await parser.aload_data(file_path)

    print(f"[DEBUG-INGEST] LlamaParse returned {len(documents)} document objects")

    pages = []

    for i, doc in enumerate(documents, start=1):
        text = doc.text.strip()

        if len(text.split()) < 10:
            print(f"[DEBUG-INGEST] Skipping page {i} due to low word count (< 10 words)")
            continue

        meta = getattr(doc, "metadata", {}) or {}

        page = (
            meta.get("page_number")
            or meta.get("page")
            or i   # fallback index
        )

        pages.append({
            "page": page,
            "text": text,
        })

    print(f"[DEBUG-INGEST] Parsing complete. Extracted {len(pages)} valid pages.")
    if pages:
        print(f"[DEBUG-INGEST] Sample output (first 100 chars): {pages[0]['text'][:100].replace(chr(10), ' ')}")
        
    return pages
