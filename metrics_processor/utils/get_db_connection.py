from mysql.connector import connect
import logging
from fastapi import HTTPException

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection(host:str, port:int, user:str, password:str, database:str=None):
    try:
        connection_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password
        }
        if database:
            connection_params["database"] = database
        
        cnx = connect(**connection_params)
        logger.info("Successfully connected to DB")
    except Exception as e:
        logger.error(f"Error connecting to DB: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error connecting to DB: {str(e)}")
    
    return cnx