import os
from pydantic import BaseSettings

import logging

class Settings(BaseSettings):
    
    kafka_server: str
    kafka_port: str
    kafka_groupId: str
    kafka_topic: str

    temporal_server: str
    temporal_namespace: str = "default"
    temporal_queuename: str
    
    temporal_task_init_interval: float = 3
    temporal_task_backoff_coefficient: float = 2.0  
    temporal_task_max_attempts: int = 3
    temporal_task_max_interval: float = 10

    cassandra_server: str = "cassandra"
    cassandra_port: int = 9042

    notification_date_format: str = "%Y-%m-%d UTC %H:%M:%S"

settings = Settings()

workflow_definition_files_path = "./Workflows_Definition_Files" 

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./WORKFLOW_MS.log', filemode='w')

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