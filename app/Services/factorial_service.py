from workflows.factorial_workflow import FactorialFlow
from temporalClient import TemporalClient
from config import logger as log
from config import settings as config
import uuid

async def invokeFactorialWorkflow(number: int) -> str :
    log.info(f"invokeFactorialWorkflow {number}")

    client = await TemporalClient.get_instance()

    result = await client.execute_workflow(
        FactorialFlow.run, number, id=("FactorialWorkflow_"+str(uuid.uuid4())), task_queue=config.temporal_queue_name
    )

    return result