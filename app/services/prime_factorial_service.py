from workflows.prime_factorial_workflow import PrimeFactorialFlow
from temporalClient import TemporalClient
from config import logger as log
from config import settings as config
import uuid

async def invokePrimeFactorialWorkflow(number: int) -> str :
    log.info(f"invokePrimeWorkflow {number}")

    client = await TemporalClient.get_instance()

    result = await client.execute_workflow(
        PrimeFactorialFlow.run, number, id=("PrimeFactorialFlow_"+str(uuid.uuid4())), task_queue=config.temporal_queue_name
    )

    return result