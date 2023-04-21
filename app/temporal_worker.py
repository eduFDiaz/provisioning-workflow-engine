# temporal_worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

async def run_temporal_worker(client, task_queue, workflows, activities):
    worker = Worker(client, task_queue=task_queue, workflows=workflows, activities=activities)
    await worker.run()

async def start_temporal_worker(temporal_address, namespace, task_queue, workflows, activities):
    client = await Client.connect(temporal_address, namespace=namespace)
    asyncio.create_task(run_temporal_worker(client, task_queue, workflows, activities))
    print("Temporal worker started.")
