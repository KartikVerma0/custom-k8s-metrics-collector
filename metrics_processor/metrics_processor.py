from fastapi import FastAPI, HTTPException
from models.node_metrics_model import NodeMetricsList
from utils.convert_nano_to_milli_cores import convert_nano_to_milli_cores
from utils.convert_ki_to_mi import convert_ki_to_mi
from dotenv import load_dotenv
from utils.get_db_connection import get_db_connection
import os
import logging
from utils.convert_time_to_mysql_format import convert_time_to_mysql_format

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

@app.post("/node_metrics")
async def root(nodeMetrics: NodeMetricsList):
    _nodeMetrics = nodeMetrics.model_dump()
    
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    if not all([db_host, db_port, db_user, db_password]):
        logger.error("Missing required database environment variables")
        raise HTTPException(status_code=500, detail="Missing required database environment variables")
    
    logger.debug(f"Connecting to DB: host={db_host}, port={db_port}, user={db_user}")
    cnx = get_db_connection(
        host=db_host,
        port=int(db_port),
        user=db_user,
        password=db_password
    )
    
    insert_statement = ""
    for item in _nodeMetrics["items"]:
        _nodeName = item["metadata"]["name"]
        _timestamp = item["timestamp"]
        _cpuUsageNanocores = item["usage"]["cpu"]
        _memoryUsageKi = item["usage"]["memory"]
        
        mysql_timestamp = convert_time_to_mysql_format(_timestamp)
        
        _cpuUsageMillicores = convert_nano_to_milli_cores(_cpuUsageNanocores)
        _memoryUsageMi = convert_ki_to_mi(_memoryUsageKi)
        
        insert_statement = insert_statement + f"VALUES ('{_nodeName}', {_cpuUsageMillicores}, {_memoryUsageMi}, '{mysql_timestamp}'), \n"
    
    insert_statement = insert_statement.rstrip(', \n')
    try:
        sql_operation = f'''
        INSERT INTO nodes.node_metrics (node_name, cpu_millicores, memory_mb, collected_at)
        {insert_statement}
        '''
        print(sql_operation)
        cur = cnx.cursor()
        cur.execute(sql_operation)
        cnx.commit()
        cur.close()
        cnx.close()
        logger.info("Successfully inserted/updated node metrics data to DB")
    except Exception as e:
        logger.error(f"Problem inserting node metrics data to DB: {str(e)}")
        cnx.rollback()
        cnx.close()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    # print(_timestamp, _nodeName, f"{_cpuUsageMillicores:.2f}m", f"{_memoryUsageMi:.2f}Mi")
    
    return {"message": "Got the node metrics"}