from temporalio.client import Client
from config import settings
import asyncio
from config import logger as log

class TemporalClient:
    _instance = None

    @staticmethod
    async def get_instance():
        if TemporalClient._instance is None:
            while True:
                try:
                    TemporalClient._instance = await Client.connect(
                        settings.temporal_server, namespace=settings.temporal_namespace
                    )
                    break  # Connected successfully, exit the loop.
                except Exception as e:
                    log.debug(f"Failed to connect to Temporal server due to {str(e)}, retrying in 5 seconds...")
                    await asyncio.sleep(5)  # Wait for 5 seconds before retrying
        return TemporalClient._instance

    def __init__(self):
        raise RuntimeError("Call get_instance() instead")