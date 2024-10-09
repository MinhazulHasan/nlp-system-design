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


# async def get_pdf_content(url: str, timeout: int = 30, max_retries: int = 3) -> Optional[bytes]:

#     headers: Dict[str, str] = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#     }
    
#     async def download_with_session(session: aiohttp.ClientSession) -> Optional[bytes]:
#         try:
#             async with session.get(url, allow_redirects=True, headers=headers) as response:
#                 if response.status == 200:
#                     content_type = response.headers.get('Content-Type', '').lower()
#                     if 'application/pdf' in content_type:
#                         return await response.read()
#                     else:
#                         report_logger.warning(f"URL {url} does not point to a PDF. Content-Type: {content_type}")
#                 elif response.status == 403:
#                     report_logger.error(f"Access forbidden for {url}. May require authentication or have access restrictions.")
#                 else:
#                     report_logger.error(f"Failed to download PDF from {url}. Status: {response.status}")
#                 return None
#         except aiohttp.ClientError as e:
#             report_logger.error(f"Network error while downloading PDF from {url}: {str(e)}")
#         except asyncio.TimeoutError:
#             report_logger.error(f"Timeout while downloading PDF from {url}")
#         except Exception as e:
#             report_logger.error(f"Unexpected error while downloading PDF from {url}: {str(e)}")
#         return None

#     for attempt in range(max_retries):
#         try:
#             timeout_obj = ClientTimeout(total=timeout * (attempt + 1))  # Increase timeout with each retry
#             async with aiohttp.ClientSession(timeout=timeout_obj) as session:
#                 result = await download_with_session(session)
#                 if result:
#                     return result
#         except Exception as e:
#             report_logger.error(f"Session creation failed for {url}: {str(e)}")
        
#         wait_time = min(2 ** attempt, 60)  # Cap wait time at 60 seconds
#         report_logger.info(f"Retrying download for {url} in {wait_time} seconds...")
#         await asyncio.sleep(wait_time)
    
#     report_logger.error(f"All attempts to download {url} failed.")
#     return None


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