import os
import logging
from pydantic import BaseSettings

FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./CONSUMER_MS.log', filemode='a')

# Create an instance of the logger
logger = logging.getLogger()

def is_running_in_docker():
    return os.path.exists('/.dockerenv')

class Settings(BaseSettings):
    kafka_server: str
    kafka_port: str = "9092"
    kafka_groupId: str = "group-default"
    
    cassandra_host: str
    cassandra_port : str = 9042
    cassandra_user: str
    cassandra_password: str
    
settings = Settings()