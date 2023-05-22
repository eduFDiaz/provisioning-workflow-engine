import os
import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='./CONSUMER_MS.log', filemode='a')

# Create an instance of the logger
logger = logging.getLogger()

def is_running_in_docker():
    return os.path.exists('/.dockerenv')