import os
from typing_extensions import override
from motor.motor_asyncio import AsyncIOMotorClient
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

from contextvars import Context, ContextVar, copy_context

api_credentials = {
    'REST': {
        'username': 'admin',
        'password': 'C1sco12345',
        'paramsFile': './Models/PARAMS/REST_PARAMS.yml'
    },
    'CLI': {
        'username': 'admin',
        'password': 'C1sco12345',
        'paramsFile': './Models/PARAMS/CLI_PARAMS.yml'
    },
    'NETCONF': {
        'username': 'admin',
        'password': 'C1sco12345',
        'paramsFile': './Models/PARAMS/NETCONF_PARAMS.yml'
    },
    'GRPC': {
        'username': 'grpc_user',
        'password': 'grpc_pass',
        'paramsFile': './Models/PARAMS/GRPC_PARAMS.yml'
    }
}