import aiohttp
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from app.utilities.hashfinder import hash_file
from app.services.embedding_service import split_documents, add_to_chroma
from io import BytesIO


async def get_pdf_content(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Failed to download PDF from {url}. Status: {response.status}")


async def process_pdf(info: tuple):
    company_name, pdf_name, pdf_link, pdf_date = info
    content = await get_pdf_content(pdf_link)
    
    file_hash = hash_file(BytesIO(content))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        chunks = split_documents(documents)
        await add_to_chroma(chunks, pdf_name, file_hash)
        return file_hash, content  # Return the file_hash and content
    finally:
        os.unlink(temp_file_path)  # Ensure temporary file is deleted