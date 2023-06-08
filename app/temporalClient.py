from temporalio.client import Client
from config import configs


class TemporalClient:
    _instance = None

    @staticmethod
    async def get_instance():
        if TemporalClient._instance is None:
            TemporalClient._instance = (await Client.connect(configs.get("temporal.server").data, namespace=configs.get("temporal.namespace").data))
        return TemporalClient._instance

    def __init__(self):
        raise RuntimeError("Call get_instance() instead")