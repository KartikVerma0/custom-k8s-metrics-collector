#!/usr/bin/env python3
"""
Script to set up MySQL Event Scheduler for TTL cleanup.
This creates an event that automatically deletes metrics older than 30 minutes.
"""

import os
import sys
from dotenv import load_dotenv
from utils.get_db_connection import get_db_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def setup_ttl_event():
    """Set up MySQL Event Scheduler to delete old metrics"""
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "nodes")  # Default to "nodes" if not specified
    
    if not all([db_host, db_port, db_user, db_password]):
        logger.error("Missing required database environment variables")
        sys.exit(1)
    
    try:
        cnx = get_db_connection(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        cur = cnx.cursor()
        
        # Enable event scheduler
        logger.info("Enabling MySQL Event Scheduler...")
        cur.execute("SET GLOBAL event_scheduler = ON")
        
        # Drop existing event if it exists
        logger.info("Dropping existing event if it exists...")
        cur.execute("DROP EVENT IF EXISTS cleanup_old_node_metrics")
        
        # Create the cleanup event
        logger.info("Creating cleanup event...")
        create_event_sql = f"""
        CREATE EVENT cleanup_old_node_metrics
        ON SCHEDULE EVERY 5 MINUTE
        DO
          DELETE FROM {db_name}.node_metrics 
          WHERE collected_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
        """
        cur.execute(create_event_sql)
        
        # Verify the event was created
        cur.execute("SHOW EVENTS LIKE 'cleanup_old_node_metrics'")
        result = cur.fetchone()
        
        if result:
            logger.info("✓ TTL event created successfully!")
            logger.info(f"  Event name: {result[1]}")
            logger.info(f"  Status: {result[8]}")
            logger.info("  The event will run every 5 minutes to delete metrics older than 30 minutes")
        else:
            logger.warning("Event was created but could not be verified")
        
        cnx.commit()
        cur.close()
        cnx.close()
        
    except Exception as e:
        logger.error(f"Error setting up TTL event: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_ttl_event()

