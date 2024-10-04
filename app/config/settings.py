#Load environment variables and other configurations
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ID = os.getenv('GOOGLE_SEARCH_ID')

BUCKET_ARN = os.getenv('BUCKET_ARN')
BUCKET_NAME = os.getenv('BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'eu-west-2')

HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
