from fastapi import APIRouter, HTTPException
from app.services.search_service import fetch_pdf_links
from app.services.search_service_v2 import fetch_pdf_links_v2
from app.services.embedding_service import get_similar_documents, get_similar_documents_v2
from langchain.prompts import ChatPromptTemplate
from app.services.openai_service import openai_response
from app.core.prompt import get_prompt, get_prompt_for_snippet, get_prompt_for_specific_field
from app.utilities.helper import save_file, save_file_v2
from app.utilities.logger import report_logger
from app.services.pdf_service import get_pdf_content, get_pdf_hash, embed_pdf, embed_pdf_v2
from app.database.operations.document_storage import check_document_exists, insert_document
from typing import List, Tuple, Optional
from pathlib import Path
import json
import pandas as pd

VALID_FOLDER = "valid"
INVALID_FOLDER = "invalid"


extraction_router = APIRouter()


async def document_check_and_DB_insertion(info: Tuple[str, str, str, Optional[str], Optional[str]]) -> Optional[str]:
    company_name, pdf_name, pdf_link, pdf_date, snippet = info
    try:
        content = await get_pdf_content(pdf_link)
        file_hash = await get_pdf_hash(content)
        
        if await check_document_exists(file_hash):
            report_logger.info(f"Document {pdf_name} already exists in the database. Skipping.")
            return None
        
        await insert_document(company_name, pdf_name, pdf_link, pdf_date, file_hash)
        report_logger.info(f"Document {pdf_name} processed and inserted into the database.")
        return file_hash
    
    except Exception as e:
        report_logger.error(f"Error processing document {pdf_name}: {str(e)}")
        return None



@extraction_router.post('/validate_using_snippet', status_code=201)
async def validate_using_snippet(company_name: str):
    try:
        pdf_info = await fetch_pdf_links_v2(company_name, 2)
        for info in pdf_info:
            company_name, pdf_name, pdf_link, pdf_date, snippet = info
            file_hash = await document_check_and_DB_insertion(info)
            if file_hash:
                query = f"Is the Document valid for the company: '{company_name}'"
                prompt_template = ChatPromptTemplate.from_template(get_prompt_for_snippet())
                prompt = prompt_template.format(query=query, pdf_name=pdf_name, pdf_link={pdf_link}, snippet=snippet)
                response_text = await openai_response(prompt)
                if "YES" in response_text.upper():
                    full_path = Path("collected_documents_v2") / company_name / VALID_FOLDER / pdf_name
                    await save_file_v2(company_name, pdf_name, pdf_link, True)
                    await embed_pdf_v2(full_path, file_hash, company_name)
                    report_logger.info(f"Document {pdf_name} is valid and saved to the valid folder")
                else:
                    await save_file_v2(company_name, pdf_name, pdf_link, False)
                    report_logger.info(f"Document {pdf_name} is invalid and saved to the invalid folder")
        return { "message": pdf_info }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@extraction_router.post('/get_report')
async def get_report(company_name: str):
    try:
        with open('output.json', 'r') as json_file:
            data = json.load(json_file)
        
        all_responses = []

        for record in data:
            query = f"{record.get('Data Field', '')} of {company_name}"

            # Perform the Chroma DB similarity search for the specific query
            context = await get_similar_documents_v2(company_name, query)

            # Format the prompt using the updated prompt template
            prompt_template = ChatPromptTemplate.from_template(get_prompt_for_specific_field())
            prompt = prompt_template.format(context=context, query=query, query_description=record.get('Description', ''), expected_values=record.get('Expected values', 'Not Defined'))

            # Get the OpenAI response for this query
            response_text = await openai_response(prompt)
            print(f"The response from OpenAI for query '{query}': {response_text}")

            # Append the response to the all_responses list
            all_responses.append({
                "query": query,
                "response": response_text
            })

            # Convert the list of dictionaries to a pandas DataFrame
            df = pd.DataFrame(all_responses)
            # Save the DataFrame to a CSV file
            df.to_csv('responses.csv', index=False, encoding='utf-8')

        # Return all responses as a single output
        return { "results": all_responses }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
