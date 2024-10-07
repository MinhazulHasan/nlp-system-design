import aiohttp
from app.config.settings import config
from app.utilities.helper import generate_query, sanitize_filename, preprocess_datetime


async def fetch_pdf_links(company_name: str):
    query = generate_query(company_name)
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': config.GOOGLE_API_KEY,
        'cx': config.GOOGLE_SEARCH_ID,
        'q': query,
        'fileType': 'pdf',
        'num': 10
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
    
    links = []
    if 'items' in data:
        for item in data['items']:
            creation_date_time = preprocess_datetime(item['pagemap']['metatags'][0]['creationdate'])
            filename = sanitize_filename(item['title'])
            links.append((
                company_name,
                filename,
                item['link'],
                creation_date_time
            ))
    return links
