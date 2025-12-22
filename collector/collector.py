from kubernetes import client, config
import os
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config.load_incluster_config()

def metrics_resolution_validator():
    _metrics_resolution_str = os.getenv("METRICS_RESOLUTION_TIME")

    if _metrics_resolution_str == None:
        return 15

    try:
        _metrics_resolution = int(_metrics_resolution_str)
    except ValueError:
        logger.error("Error parsing metrics resolution to integer")
        logger.info("Setting metrics resolution to 15s")
        _metrics_resolution = 15
    
    if _metrics_resolution <15:
        logger.warning("Metrics resolution too low. Setting metrics resolution to 15s")
        metrics_resolution = 15
    else:
        metrics_resolution = _metrics_resolution
    
    return metrics_resolution

def scrap_node_metrics():
    with client.ApiClient() as api_client:
        api_instance = client.CustomObjectsApi(api_client)
        group = "metrics.k8s.io"
        version = "v1beta1"
        plural = "nodes"
        api_response = api_instance.list_cluster_custom_object(group, version, plural)
        logger.debug(api_response)

def scheduler():
    while True:
        scrap_node_metrics()
        metrics_resolution = metrics_resolution_validator()
        time.sleep(metrics_resolution)
    
if __name__ == "__main__":
    scheduler()


