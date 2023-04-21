import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

import logging

MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "mydb")
MONGO_COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME", "mycollection")
MONGO_USER = os.environ.get("MONGO_USER", "admin")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "your_password")
TEMPORAL_URL = os.environ.get("TEMPORAL_URL", "temporal:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "default")
TEMPORAL_QUEUE_NAME = os.environ.get("TEMPORAL_QUEUE_NAME", "test-queue")

class Settings(BaseSettings):
    mongodb_url: str = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    mongodb_db_name: str = MONGO_DB_NAME
    temporal_url: str = TEMPORAL_URL
    temporal_namespace: str = TEMPORAL_NAMESPACE
    temporal_queue_name: str = TEMPORAL_QUEUE_NAME

settings = Settings()

db_client = AsyncIOMotorClient(settings.mongodb_url)
database = db_client[settings.mongodb_db_name]
temporal_url = settings.temporal_url
temporal_namespace = settings.temporal_namespace
temporal_queue_name = settings.temporal_queue_name

import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create an instance of the logger
logger = logging.getLogger(__name__)