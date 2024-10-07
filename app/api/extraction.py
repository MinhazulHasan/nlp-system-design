from fastapi import APIRouter, HTTPException
from app.services.search_service import fetch_pdf_links
from app.services.pdf_service import process_pdf
from app.services.embedding_service import get_similar_documents
from langchain.prompts import ChatPromptTemplate
from app.services.openai_service import openai_response
from app.core.prompt import get_prompt
from app.utilities.helper import save_file
from app.utilities.logger import report_logger

extraction_router = APIRouter()

@extraction_router.post('/fetch_doc_and_validate', status_code=201)
async def fetch_doc_and_validate(company_name: str):
    try:
        pdf_info = await fetch_pdf_links(company_name)
        report_logger.info(f"PDF links fetched for {company_name} are:\n{pdf_info}")
        processed_docs = []

        for info in pdf_info:
            file_hash, content = await process_pdf(info)
            if file_hash:
                query = f"ESG Report for {company_name}"
                similar_docs = await get_similar_documents(file_hash, query)
                processed_docs.append({
                    "pdf_info": info,
                    "file_hash": file_hash
                })

                prompt_template = ChatPromptTemplate.from_template(get_prompt())
                prompt = prompt_template.format(context=similar_docs, question=query)
                response_text = await openai_response(prompt)
                report_logger.info(f"For the document {info[1]}\nThe response from OpenAI is {response_text}")
                
                company_name, pdf_name, pdf_link, pdf_date = info
                if response_text.lower() == "valid":
                    print("Document is valid")
                    save_file(content, pdf_name, company_name, True)
                    report_logger.info(f"Document {pdf_name} is valid and saved to the valid folder")
                else:
                    print("Document is invalid")
                    save_file(content, pdf_name, company_name, False)
                    report_logger.info(f"Document {pdf_name} is invalid and saved to the invalid folder")
    
        return { "message": "Documents fetched and processed successfully",
                 "processed_docs": processed_docs }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
