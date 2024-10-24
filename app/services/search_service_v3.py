import aiohttp
from app.config.settings import config
from typing import List, Tuple, Optional, Any, Dict
from app.utilities.helper import sanitize_filename, preprocess_datetime
from app.utilities.logger import report_logger
import asyncio

async def fetch_pdf_links_v3(
        company_name: str,
        start_year: int = 2019,
        end_year: int = 2023,
        num_pages: int = 2
    ) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:

    all_results = []
    
    for year in range(end_year, start_year - 1, -1):
        report_logger.info(f"Fetching ESG reports for {company_name} for year {year}")
        year_results = await fetch_pdf_links_for_year(company_name, year, num_pages)
        all_results.extend(year_results)
        
        # Add a small delay between years to avoid rate limiting
        await asyncio.sleep(1)
    
    return all_results

async def fetch_pdf_links_for_year(company_name: str, year: int, num_pages: int) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:
    
    query = f'"ESG report" for "{company_name}" at the year "{year}"'
    url = "https://www.googleapis.com/customsearch/v1"
    year_results: List[Dict[str, Any]] = []

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
                        report_logger.error(f"Failed to fetch data for {company_name} ({year}). Status Code: {response.status}")
                        continue
                    data = await response.json()
                    
                    if 'error' in data:
                        report_logger.error(f"API error for {company_name} ({year}): {data['error'].get('message')}")
                        continue
                        
        except aiohttp.ClientError as e:
            report_logger.error(f"Network error occurred for {company_name} ({year}): {e}")
            continue
        except Exception as e:
            report_logger.error(f"An error occurred for {company_name} ({year}): {e}")
            continue
        
        if 'items' in data:
            year_results.extend(data['items'])
        else:
            report_logger.warning(f"No more results found for {company_name} ({year}) after page {i + 1}")
            break

    return parse_response(year_results, company_name)

# The parse_response function remains unchanged
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