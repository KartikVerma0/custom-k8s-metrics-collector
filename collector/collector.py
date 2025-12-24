from kubernetes import client, config
import os
import logging
import time
import argparse
import requests


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_arg_parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev",action="store_true", help="Enables dev mode")
    args = parser.parse_args()
    return args

args = setup_arg_parsing()

if args.dev == True:
    from dotenv import load_dotenv
    load_dotenv()
    config.load_kube_config()
else:
    config.load_incluster_config()

def metrics_resolution_validator():
    _metrics_resolution_str = os.getenv("METRICS_RESOLUTION_TIME")

    if _metrics_resolution_str == None:
        logger.error("No metrics resolution time provided.")
        logger.info("Setting metrics resolution to 15s")
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
        send_metrics_to_metrics_processor(api_response)

def get_metrics_processor_service_url():
    if (args.dev == False):
        service_name = os.getenv("METRICS_PROCESSOR_SERVICE") if os.getenv("METRICS_PROCESSOR_SERVICE") else "metrics_processor"
        service_namespace = os.getenv("METRICS_PROCESSOR_SERVICE_NAMESPACE") if os.getenv("METRICS_PROCESSOR_SERVICE_NAMESPACE") else "custom-metrics-collection"
        service_port = int(os.getenv("METRICS_PROCESSOR_SERVICE_PORT")) if os.getenv("METRICS_PROCESSOR_SERVICE_PORT") else 9376
        return f"http://{service_name}.{service_namespace}:{service_port}"
    else:
        return os.getenv("METRICS_PROCESSOR_URL")

def send_metrics_to_metrics_processor(metrics):
    url = get_metrics_processor_service_url() + "/node_metrics"
    try:
        response = requests.post(url, json=metrics, timeout=10)
        if args.dev == True: 
            logger.debug(f"Response status Code: {response.status_code}")
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Problem sending metrics data to metrics_processor: {str(e)}")

def scheduler():
    metrics_resolution = metrics_resolution_validator()
    while True:
        scrap_node_metrics()
        time.sleep(metrics_resolution)

if __name__ == "__main__":
    scheduler()