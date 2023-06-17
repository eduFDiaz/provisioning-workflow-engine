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
    
    temporal_task_init_interval: float
    temporal_task_backoff_coefficient: float
    temporal_task_max_attempts: int
    temporal_task_max_interval: float
    temporal_task_start_to_close_timeout: float
    temporal_workflow_execution_timeout: float
    
    cassandra_host: str
    cassandra_port : str = 9042
    cassandra_user: str
    cassandra_password: str
    
    ssh_timeout: int = 5
    ssh_banner_timeout: int = 5
    ssh_auth_timeout: int = 5
    
    consumer_app_host: str
    consumer_app_port: str
    

    notification_date_format: str = "%Y-%m-%d UTC %H:%M:%S"

    repo_access_token: str = "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"

settings = Settings()

workflow_definition_files_path = "./Workflows_Definition_Files" 

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./SANDBOX_WORKFLOW_MS.log', filemode='w')

# Create an instance of the logger
logging.getLogger('github').setLevel(logging.ERROR)
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