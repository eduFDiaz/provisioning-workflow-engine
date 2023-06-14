import os
from pydantic import BaseSettings

import logging

class Settings(BaseSettings):
    pass

settings = Settings()

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./CONFIG_MS.log', filemode='w')

# Create an instance of the logger
logger = logging.getLogger()