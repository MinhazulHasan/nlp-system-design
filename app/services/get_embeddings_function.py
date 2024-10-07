from langchain_openai import OpenAIEmbeddings
from app.config.settings import config


def get_embeddings_function():
    embedding = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
    return embedding
