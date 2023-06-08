import os
from pydantic import BaseSettings

import logging

def is_running_in_docker():
    return os.path.exists('/.dockerenv')

TEMPORAL_URL = None
if is_running_in_docker():
    TEMPORAL_URL = os.environ.get("TEMPORAL_URL", "temporal:7233")
else:
    TEMPORAL_URL = os.environ.get("TEMPORAL_URL", "localhost:7233")

MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "default")
TEMPORAL_QUEUE_NAME = os.environ.get("TEMPORAL_QUEUE_NAME", "test-queue")
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "memgraph")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", 7687))

class Settings(BaseSettings):
    temporal_url: str = TEMPORAL_URL
    temporal_namespace: str = TEMPORAL_NAMESPACE
    temporal_queue_name: str = TEMPORAL_QUEUE_NAME
    memgraph_host: str = MEMGRAPH_HOST
    memgraph_port: int = MEMGRAPH_PORT

settings = Settings()

temporal_url = settings.temporal_url
temporal_namespace = settings.temporal_namespace
temporal_queue_name = settings.temporal_queue_name
memgraph_host = settings.memgraph_host
memgraph_port = settings.memgraph_port

workflow_definition_files_path = "./Workflows_Definition_Files" 

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./WORKFLOW_MS.log', filemode='a')

# Create an instance of the logger
logger = logging.getLogger()

api_credentials = {
    'REST': {
        'username': 'admin',
        'password': 'C1sco12345'
    },
    'CLI': {
        'username': 'admin',
        'password': 'C1sco12345'
    },
    'NETCONF': {
        'username': 'admin',
        'password': 'C1sco12345'
    },
    'GRPC': {
        'username': 'grpc_user',
        'password': 'grpc_pass'
    }
}