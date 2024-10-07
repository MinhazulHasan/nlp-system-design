from fastapi import APIRouter, HTTPException
from app.services.search_service import fetch_pdf_links
from app.services.pdf_service import process_pdf
from app.services.embedding_service import get_similar_documents
from langchain.prompts import ChatPromptTemplate
from app.services.openai_service import openai_response
from app.core.prompt import get_prompt
from app.utilities.helper import save_file

extraction_router = APIRouter()

@extraction_router.post('/fetch_doc_and_validate', status_code=201)
async def fetch_doc_and_validate(company_name: str):
    try:
        pdf_info = await fetch_pdf_links(company_name)
        processed_docs = []

        for info in pdf_info:
            file_hash, content = await process_pdf(info)
            if file_hash:
                query = f"ESG Report for {company_name}"
                similar_docs = await get_similar_documents(file_hash, query)
                processed_docs.append({
                    "pdf_info": info,
                    "file_hash": file_hash,
                    "similar_documents": similar_docs
                })

                prompt_template = ChatPromptTemplate.from_template(get_prompt())
                prompt = prompt_template.format(context=similar_docs, question=query)
                response_text = await openai_response(prompt)
                print(f'response_text: {response_text}')
                
                if response_text.lower() == "valid":
                    print("Document is valid")
                    company_name, pdf_name, pdf_link, pdf_date = info
                    save_file(content, pdf_name, company_name)
                else:
                    print("Document is invalid")
    
        return { "message": "Documents fetched and processed successfully",
                 "processed_docs": processed_docs }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
