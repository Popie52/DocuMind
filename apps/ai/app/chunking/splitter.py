from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=500,
    chunk_overlap=60,
    separators=[
        "\n# ",
        "\n## ",
        "\n### ",
        "\n#### ",
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)

def split_text(text: str) -> list[str]:
    return splitter.split_text(text)