from temporalio.client import Client
from config import settings

class TemporalClient:
    _instance = None

    @staticmethod
    async def get_instance():
        if TemporalClient._instance is None:
            TemporalClient._instance = (await Client.connect(settings.temporal_url, namespace=settings.temporal_namespace))
        return TemporalClient._instance

    def __init__(self):
        raise RuntimeError("Call get_instance() instead")