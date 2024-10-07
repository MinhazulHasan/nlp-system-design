import aiohttp
from app.config.settings import config
from typing import List, Tuple, Optional
from app.utilities.helper import generate_query, sanitize_filename, preprocess_datetime
from app.utilities.logger import report_logger


async def fetch_pdf_links(company_name: str) -> List[Tuple[str, str, str, Optional[str]]]:
    query = generate_query(company_name)
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': config.GOOGLE_API_KEY,
        'cx': config.GOOGLE_SEARCH_ID,
        'q': query,
        'fileType': 'pdf',
        'num': 10
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status != 200:
                    report_logger.error(f"Failed to fetch data from Google API. Status Code: {response.status}")
                    return []
                data = await response.json()
    except aiohttp.ClientError as e:
        report_logger.error(f"Network error occurred: {e}")
        return []
    except Exception as e:
        report_logger.error(f"An error occurred: {e}")
        return []

    return parse_response(data, company_name)


def parse_response(data: dict, company_name: str) -> List[Tuple[str, str, str, Optional[str]]]:
    links = []
    try:
        if 'items' in data:
            for item in data['items']:
                title = item.get('title', 'Unnamed Document')
                link = item.get('link', '')

                if 'pagemap' in item and 'metatags' in item['pagemap'] and 'creationdate' in item['pagemap']['metatags'][0]:
                    creation_date_time = preprocess_datetime(item['pagemap']['metatags'][0]['creationdate'])
                else:
                    creation_date_time = None

                filename = sanitize_filename(title)
                links.append((company_name, filename, link, creation_date_time))
        else:
            report_logger.warning(f"No items found in the API response for {company_name}")
    except KeyError as e:
        report_logger.error(f"Unexpected structure in the API response: {e}")
    
    return links
