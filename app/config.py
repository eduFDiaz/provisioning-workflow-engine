import os
from pydantic import BaseSettings

import logging
        
def is_running_in_docker():
    return os.path.exists('/.dockerenv')

MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "default")
TEMPORAL_QUEUE_NAME = os.environ.get("TEMPORAL_QUEUE_NAME", "test-queue")
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "memgraph")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", 7687))

class Settings(BaseSettings):
    memgraph_host: str = MEMGRAPH_HOST
    memgraph_port: int = MEMGRAPH_PORT
    
    kafka_server: str
    kafka_port: str = "9092"
    kafka_groupId: str = "group-template-engine"

    temporal_server: str
    temporal_namespace: str = "default"
    temporal_queuename: str
    
    temporal_task_init_interval: float = 3
    temporal_task_backoff_coefficient: float = 2.0  
    temporal_task_max_attempts: int = 3
    temporal_task_max_interval: float = 10

settings = Settings()

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