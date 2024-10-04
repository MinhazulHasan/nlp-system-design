import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.services.get_embeddings_function import get_embeddings_function


CHROMA_PATH = "chroma"
DATA_PATH = "data"


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], file_name: str, file_hash: str):
    # Load the existing database.
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings_function())

    # Embed hash in metadata and generate meaningful IDs
    chunks_with_hash, new_chunk_ids = embed_hash_in_metadata(chunks, file_name, file_hash)

    # Check if documents with this file_hash already exist
    existing_docs = db.get(where={"file_hash": file_hash})

    if existing_docs["ids"]:
        print(f"✅ Documents with file hash {file_hash} already exist. Skipping addition.")
        return

    # If we reach here, it means no documents with this file_hash exist
    print(f"👉 Adding new documents: {len(chunks_with_hash)}")
        
    # Add the documents
    db.add_documents(chunks_with_hash, ids=new_chunk_ids)
    db.persist()


def embed_hash_in_metadata(chunks: list[Document], file_name: str, file_hash: str) -> tuple[list[Document], list[str]]:
    new_chunk_ids = []
    for i, chunk in enumerate(chunks):
        # Embed hash in metadata
        chunk.metadata["file_hash"] = file_hash
        chunk_id = f"{file_name}_{i+1}"
        new_chunk_ids.append(chunk_id)

    return chunks, new_chunk_ids


def get_similar_documents_from_chroma(hash: str, query: str):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings_function())
    similar_documents = db.similarity_search_with_score(query, k=3, filter={"file_hash": hash})
    formatted_results = [
        {
            "page_content": result[0].page_content,
            "score": result[1]
        }
        for result in similar_documents
    ]
    return formatted_results