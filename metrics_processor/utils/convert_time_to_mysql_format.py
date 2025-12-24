from datetime import datetime
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_time_to_mysql_format(time):
    try:
        # Parse ISO 8601 format (e.g., '2025-12-24T10:57:07Z')
        # Replace 'Z' (UTC) with '+00:00' for fromisoformat compatibility
        timestamp_str = time.replace('Z', '+00:00')
        dt = datetime.fromisoformat(timestamp_str)
        # Format as MySQL datetime: YYYY-MM-DD HH:MM:SS
        mysql_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Error parsing timestamp {time}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {time}")
    return mysql_timestamp