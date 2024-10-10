from datetime import datetime, timedelta
import requests
from pathlib import Path
from typing import Union
from app.utilities.logger import report_logger
import aiohttp


# Constants for folder names
VALID_FOLDER = "valid"
INVALID_FOLDER = "invalid"



def generate_query(company: str) -> str:
    return f'"{company}" "company report"'



def sanitize_filename(filename):
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        filename = filename.replace(char, '_')
    return filename[:200] + '.pdf'



def preprocess_datetime(date_str):
    try:
        if "'" in date_str:
            return (datetime.strptime(date_str[2:16], '%Y%m%d%H%M%S') - timedelta(hours=int(date_str[16:19]))).strftime('%Y-%m-%d %H:%M:%S')

        elif date_str.endswith('Z'):
            return datetime.strptime(date_str[2:16], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')

        else:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e:
        print(f"Error for date-time conversion: {e}\nOriginal date: {date_str}")
        return None



def download_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        print(f"Responnse : {response}")
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading {url}: {e}")
        return None



def create_folder_structure(company: str) -> None:
    base_path = Path("collected_documents") / company
    for folder in [VALID_FOLDER, INVALID_FOLDER]:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)



def save_file(content: Union[bytes, str], filename: str, company: str, is_valid: bool) -> None:
    create_folder_structure(company)
    validation_status = VALID_FOLDER if is_valid else INVALID_FOLDER
    file_path = Path("collected_documents") / company / validation_status / filename
    # Check if the file already exists
    if file_path.exists():
        report_logger.info(f"File {file_path} already exists. Skipping download.")
        return
    # Save file to the determined path
    try:
        with open(file_path, 'wb' if isinstance(content, bytes) else 'w') as f:
            f.write(content)
        report_logger.info(f"Document {file_path} is {validation_status} and saved to the {validation_status} folder.")
    except Exception as e:
        report_logger.error(f"Failed to save document {filename}. Error: {e}")



def create_folder_structure_v2(company: str) -> None:
    base_path = Path("collected_documents_v2") / company
    for folder in [VALID_FOLDER, INVALID_FOLDER]:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)



async def download_pdf_v2(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                print(f"Response : {response.status}")
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Failed to download {url}. Status code: {response.status}")
                    report_logger.error(f"Failed to download {url}. Status code: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"An error occurred while downloading {url}: {e}")
        return None



async def save_file_v2(company_name: str, pdf_name: str, pdf_link: str, is_valid: bool) -> None:
    create_folder_structure_v2(company_name)
    validation_status = VALID_FOLDER if is_valid else INVALID_FOLDER
    file_path = Path("collected_documents_v2") / company_name / validation_status / pdf_name
    # Check if the file already exists
    if file_path.exists():
        report_logger.info(f"File {file_path} already exists. Skipping download.")
        return
    
    try:
        content = await download_pdf_v2(pdf_link)
        if content:
            with open(file_path, 'wb') as f:
                f.write(content)
            report_logger.info(f"Document {pdf_name} is {validation_status} and saved to the {validation_status} folder.")
        else:
            report_logger.error(f"Failed to download {pdf_link}.")
    except Exception as e:
        report_logger.error(f"Failed to save document {pdf_name}. Error: {e}")
        