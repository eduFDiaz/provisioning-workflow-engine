# temporal_worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from config import logger as log

async def run_temporal_worker(client, task_queue, workflows, activities):
    while True:
        try:
            worker = Worker(client, task_queue=task_queue, workflows=workflows, activities=activities)
            break
        except Exception as e:
            log.debug(f"Failed to create Temporal worker due to {str(e)}, retrying in 5 seconds...")
            await asyncio.sleep(5)
    log.debug("Temporal worker created.")
    await worker.run()

async def start_temporal_worker(temporal_address, namespace, task_queue, workflows, activities):
    while True:
        try:
            client = await Client.connect(temporal_address, namespace=namespace)
            asyncio.create_task(run_temporal_worker(client, task_queue, workflows, activities))
            break
        except Exception as e:
            log.debug(f"Failed to connect to Temporal server due to {str(e)}, retrying in 5 seconds...")
            await asyncio.sleep(5)
    
    log.debug("Temporal worker started.")
