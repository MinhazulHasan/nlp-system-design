from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
import os


def get_embeddings_function():
    embedding = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'))
    return embedding
