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
    documents = await parser.aload_data(file_path)

    print(len(documents))

    pages = []

    for i, doc in enumerate(documents, start=1):
        text = doc.text.strip()

        if len(text.split()) < 10:
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

    return pages


# async def main():
#     # Assumes PDF is in: project_root/upload/sample.pdf

#     pdf_path = Path(
#     r"D:\learn\projects-ai-agents\telegram-rag-bot\apps\ai\uploads\The Go Programming Language (Alan A. A. Donovan  Brian W. Kernighan) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
# )

#     if not pdf_path.exists():
#         raise FileNotFoundError(
#             f"PDF not found: {pdf_path}"
#         )

#     pages = await parse_document(str(pdf_path))

#     print(f"\nParsed {len(pages)} pages\n")

#     # for page in pages:
#     #     print(f"\n{'=' * 50}")
#     #     print(f"PAGE {page['page']}")
#     #     print(f"{'=' * 50}")
#     #     print(page["text"][:1000])  # first 1000 chars


# if __name__ == "__main__":
#     asyncio.run(main())
