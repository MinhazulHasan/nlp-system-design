from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CHROMA_PATH: str = "chroma"
    DATA_PATH: str = "data"
    GOOGLE_API_KEY: str
    GOOGLE_SEARCH_ID: str
    BUCKET_ARN: str
    BUCKET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    HUGGING_FACE_TOKEN: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

config = Settings()
