from datetime import datetime, timedelta
import requests
import os
from pathlib import Path


def generate_query(company):
    return f"ESG documents of \"{company}\""


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
        print(f"Error : {e}")
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
    

def create_folder_structure(company: str):
    base_path = Path("collected_documents")
    folders = [""]
    for folder in folders:
        folder_path = base_path / folder / company
        folder_path.mkdir(parents=True, exist_ok=True)


def save_file(content, filename, company):
    create_folder_structure(company)
    #Save the file to data folder
    filename = f"collected_documents/{company}/{filename}.pdf"
    
    # Check if the file already exists
    if os.path.exists(filename):
        print(f"File {filename} already exists. Skipping download.")
        return
    
    with open(filename, 'wb') as f:
        f.write(content)