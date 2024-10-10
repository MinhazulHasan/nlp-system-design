from fastapi import APIRouter, HTTPException
from app.services.search_service import fetch_pdf_links
from app.services.search_service_v2 import fetch_pdf_links_v2
from app.services.embedding_service import get_similar_documents
from langchain.prompts import ChatPromptTemplate
from app.services.openai_service import openai_response
from app.core.prompt import get_prompt, get_prompt_for_snippet
from app.utilities.helper import save_file, save_file_v2
from app.utilities.logger import report_logger
from app.services.pdf_service import get_pdf_content, get_pdf_hash, embed_pdf
from app.database.operations.document_storage import check_document_exists, insert_document
from typing import List, Tuple, Optional


extraction_router = APIRouter()


async def document_check_and_DB_insertion(info: Tuple[str, str, str, Optional[str]]) -> Optional[Tuple[str, bytes]]:
    company_name, pdf_name, pdf_link, pdf_date = info
    try:
        content = await get_pdf_content(pdf_link)
        file_hash = await get_pdf_hash(content)
        
        if await check_document_exists(file_hash):
            report_logger.info(f"Document {pdf_name} already exists in the database. Skipping.")
            return None
        
        await insert_document(company_name, pdf_name, pdf_link, pdf_date, file_hash)
        report_logger.info(f"Document {pdf_name} processed and inserted into the database.")
        return file_hash, content
    
    except Exception as e:
        # report_logger.error(f"Error processing document {pdf_name}: {str(e)}")
        return None



@extraction_router.post('/fetch_doc_and_validate', status_code=201)
async def fetch_doc_and_validate(company_name: str):
    try:
        pdf_info = await fetch_pdf_links(company_name, 2)
        report_logger.info(f"PDF links fetched for {company_name} are:\n{pdf_info}")

        for info in pdf_info:
            company_name, pdf_name, pdf_link, pdf_date = info
            result = await document_check_and_DB_insertion(info)
            if result:
                file_hash, content = result
                embedding_response = await embed_pdf(info, content, file_hash)
                if embedding_response:
                    query = f"Is the Document valid for the company: '{company_name}'"
                    context = await get_similar_documents(file_hash, query)

                    prompt_template = ChatPromptTemplate.from_template(get_prompt())
                    prompt = prompt_template.format(query=query, pdf_name=pdf_name, pdf_link={pdf_link}, context=context)
                    
                    response_text = await openai_response(prompt)
                    report_logger.info(f"For the document {pdf_name}\nThe response from OpenAI is {response_text}")

                    if response_text.upper() == "YES":
                        save_file(content, pdf_name, company_name, True)
                        report_logger.info(f"Document {pdf_name} is valid and saved to the valid folder")
                    else:
                        save_file(content, pdf_name, company_name, False)
                        report_logger.info(f"Document {pdf_name} is invalid and saved to the invalid folder")
    
        return { "message": "Documents fetched and processed successfully" }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@extraction_router.post('/validate_using_snippet', status_code=201)
async def validate_using_snippet(company_name: str):
    try:
        pdf_info = await fetch_pdf_links_v2(company_name, 2)
        for info in pdf_info:
            company_name, pdf_name, pdf_link, pdf_date, snippet = info
            query = f"Is the Document valid for the company: '{company_name}'"
            prompt_template = ChatPromptTemplate.from_template(get_prompt_for_snippet())
            prompt = prompt_template.format(query=query, pdf_name=pdf_name, pdf_link={pdf_link}, snippet=snippet)
            response_text = await openai_response(prompt)
            if response_text.upper() == "YES":
                await save_file_v2(company_name, pdf_name, pdf_link, True)
                report_logger.info(f"Document {pdf_name} is valid and saved to the valid folder")
            else:
                await save_file_v2(company_name, pdf_name, pdf_link, False)
                report_logger.info(f"Document {pdf_name} is invalid and saved to the invalid folder")
        return { "message": pdf_info }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
