from motor.motor_asyncio import AsyncIOMotorClient
from Config import settings


class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self._db_client = AsyncIOMotorClient(settings.mongodb_url)
        self._database = self._db_client[settings.mongodb_db_name]

    @property
    def client(self):
        return self._db_client

    @property
    def database(self):
        return self._database

db = Database()