import aiohttp
from app.config.settings import config
from typing import List, Tuple, Optional
from app.utilities.helper import generate_query, sanitize_filename, preprocess_datetime
from app.utilities.logger import report_logger
from typing import Any, Dict

async def fetch_pdf_links_v2(company_name: str, num_pages: int = 2) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:
    query = generate_query(company_name)
    url = "https://www.googleapis.com/customsearch/v1"
    all_results: List[Dict[str, Any]] = []

    for i in range(num_pages):
        params = {
            'key': config.GOOGLE_API_KEY,
            'cx': config.GOOGLE_SEARCH_ID,
            'q': query,
            'fileType': 'pdf',
            'start': i * 10 + 1,
            'num': 10
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status != 200:
                        report_logger.error(f"Failed to fetch data from Google API. Status Code: {response.status}")
                        continue
                    data = await response.json()
        except aiohttp.ClientError as e:
            report_logger.error(f"Network error occurred: {e}")
            continue
        except Exception as e:
            report_logger.error(f"An error occurred: {e}")
            continue
        
        if 'items' in data:
            all_results.extend(data['items'])
        else:
            report_logger.warning(f"No more results found after page {i + 1}")
            break

    return parse_response(all_results, company_name)


def parse_response(data: List[Dict[str, Any]], company_name: str) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:
    links = []
    try:
        for item in data:
            title = item.get('title', 'Unnamed Document')
            link = item.get('link', '')
            snippet = item.get('snippet', 'No snippet available')

            if 'pagemap' in item and 'metatags' in item['pagemap'] and 'creationdate' in item['pagemap']['metatags'][0]:
                creation_date_time = preprocess_datetime(item['pagemap']['metatags'][0]['creationdate'])
            else:
                creation_date_time = None

            filename = sanitize_filename(title)
            links.append((company_name, filename, link, creation_date_time, snippet))
    except KeyError as e:
        report_logger.error(f"Unexpected structure in the API response: {e}")
    
    return links
