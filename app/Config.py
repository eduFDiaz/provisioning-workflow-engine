import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "mydb")
MONGO_COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME", "mycollection")
MONGO_USER = os.environ.get("MONGO_USER", "admin")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "your_password")

class Settings(BaseSettings):
    mongodb_url: str = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    mongodb_db_name: str = MONGO_DB_NAME

settings = Settings()

db_client = AsyncIOMotorClient(settings.mongodb_url)
database = db_client[settings.mongodb_db_name]
