import aiohttp
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from app.utilities.hashfinder import hash_file
from app.services.embedding_service import split_documents, add_to_chroma
from io import BytesIO
from typing import Optional, Dict, Tuple
# from aiohttp import ClientTimeout
# import asyncio
from app.utilities.logger import report_logger


async def get_pdf_content(url: str) -> Optional[bytes]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Failed to download PDF from {url}. Status: {response.status}")


async def get_pdf_hash(content: bytes) -> str:
    return hash_file(BytesIO(content))


async def embed_pdf(info: Tuple[str, str, str, Optional[str]], content: bytes, file_hash: str) -> bool:
    company_name, pdf_name, pdf_link, pdf_date = info
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        chunks = split_documents(documents)
        await add_to_chroma(chunks, pdf_name, file_hash)
        os.unlink(temp_file_path)  # Ensure temporary file is deleted
        return True
    
    except Exception as e:
        report_logger.error(f"Error embedding PDF {pdf_name}: {str(e)}")
        return False


async def embed_pdf_v2(file_path: str, file_hash: str, company_name: str) -> bool:
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        chunks = split_documents(documents)
        await add_to_chroma(chunks, file_path, file_hash, company_name)
        return True
    except Exception as e:
        report_logger.error(f"Error embedding PDF {file_path}: {str(e)}")
        return False