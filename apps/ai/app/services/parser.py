import os
from llama_parse import LlamaParse
from dotenv import load_dotenv

load_dotenv()

parser = LlamaParse(
    api_key = os.getenv('LLAMA_PARSE_API_KEY'),
    result_type = "markdown",
)

async def parse_document(
    file_path: str,
) -> str:
    documents = (        
        await parser.aload_data(
            file_path
        )
    )

    parsed_text = "\n\n".join(
        doc.text
        for doc in documents
    )

    return parsed_text