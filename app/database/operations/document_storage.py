import aioodbc
import asyncio
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRIVER = 'SQL Server'
SERVER_NAME = 'BS-1017'
DATABASE_NAME = 'HighLevelSystemDesign'

conn_string = f"""
    DRIVER={{{DRIVER}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""


async def get_connection():
    try:
        return await aioodbc.connect(dsn=conn_string, loop=asyncio.get_event_loop())
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


async def check_document_exists(file_hash: str) -> bool:
    try:
        async with await get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM NLPDocument WHERE file_hash = ?", (file_hash,))
                row = await cursor.fetchone()
                return row[0] > 0
    except Exception as e:
        logger.error(f"Error checking document existence: {e}")
        raise


async def insert_document(company_name: str, file_name: str, src_link: str, date_published: Optional[str], file_hash: str):
    try:
        async with await get_connection() as conn:
            async with conn.cursor() as cursor:
                insert_statement = """
                    INSERT INTO NLPDocument (company_name, file_name, src_link, date_published, file_hash)
                    VALUES (?, ?, ?, ?, ?)
                """
                await cursor.execute(insert_statement, (company_name, file_name, src_link, date_published, file_hash))
                await conn.commit()
                logger.info(f"Document {file_name} inserted successfully")
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        raise
