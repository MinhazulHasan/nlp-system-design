from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.services.get_embeddings_function import get_embeddings_function
from app.config.settings import config


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


async def add_to_chroma(chunks: list[Document], file_name: str, file_hash: str):
    db = Chroma(persist_directory=config.CHROMA_PATH, embedding_function=get_embeddings_function())
    chunks_with_hash, new_chunk_ids = embed_hash_in_metadata(chunks, file_name, file_hash)
    existing_docs = db.get(where={"file_hash": file_hash})
    if existing_docs["ids"]:
        return
    db.add_documents(chunks_with_hash, ids=new_chunk_ids)
    db.persist()


def embed_hash_in_metadata(chunks: list[Document], file_name: str, file_hash: str) -> tuple[list[Document], list[str]]:
    new_chunk_ids = []
    for i, chunk in enumerate(chunks):
        chunk.metadata["file_hash"] = file_hash
        chunk_id = f"{file_name}_{i+1}"
        new_chunk_ids.append(chunk_id)
    return chunks, new_chunk_ids


async def get_similar_documents(file_hash: str, query: str):
    db = Chroma(persist_directory=config.CHROMA_PATH, embedding_function=get_embeddings_function())
    similar_documents = db.similarity_search_with_score(query, k=3, filter={"file_hash": file_hash})
    return [
        {
            "page_content": result[0].page_content,
            "score": float(result[1])  # Convert to float for JSON serialization
        }
        for result in similar_documents
    ]