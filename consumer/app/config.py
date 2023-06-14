import os
import logging
from pydantic import BaseSettings

FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./CONSUMER_MS.log', filemode='w')

# Create an instance of the logger
logger = logging.getLogger()

class Settings(BaseSettings):
    kafka_server: str
    kafka_port: str
    kafka_groupId: str
    kafka_topic: str

    cassandra_host: str
    cassandra_port : str
    cassandra_user: str
    cassandra_password: str
    
settings = Settings()