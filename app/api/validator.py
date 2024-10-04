from fastapi import APIRouter, UploadFile, File
import os
import argparse
from app.services.embeddings import clear_database, load_documents, split_documents, add_to_chroma, get_similar_documents_from_chroma
from app.utilities.hashfinder import hash_file
from langchain.prompts import ChatPromptTemplate
from app.services.openai_service import openai_response


validator = APIRouter()

PROMPT_TEMPLATE = """
You are an expert AI assistant specializing in Environmental, Social, and Governance (ESG) document analysis. Your task is to determine whether a given document is a valid ESG report for a specific company based on semantic similarity search results.

Instructions:
1. Analyze the provided text chunks and their corresponding similarity scores.
2. Consider the relevance and content of each chunk in relation to the query.
3. Make a determination on whether the document is likely to be a valid ESG report for the specified company.
4. Provide ONLY a one-word response: either "valid" or "invalid".
5. Do not provide any explanation or additional context.

Remember: High similarity scores alone do not guarantee relevance. Consider the content and context of each chunk carefully.

Query: **{question}**

Similarity Search Results:
{context}

Based on these results, is this document likely to be a valid ESG report for the specified company? Respond with 'Yes' or 'No', followed by a brief explanation.
"""


@validator.post('/add_document_to_chroma')
async def add_document_to_chroma(file: UploadFile = File(...)):
    file_name, extension = file.filename.rsplit('.', 1)
    print(file_name, extension)

    file_hash = hash_file(file.file)
    print(file_hash)


    input_data_dir = "data"
    os.makedirs(input_data_dir, exist_ok=True)

    file_path = os.path.join(input_data_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()
    
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks, file_name, file_hash)
    
    return {'hash': file_hash}


@validator.post('/validate_document')
async def validate_document(hash: str, query: str):
    results = get_similar_documents_from_chroma(hash, query)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=results, question=query)
    response_text = openai_response(prompt)
    return {'response_text': response_text}
