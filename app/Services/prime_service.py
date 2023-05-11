from activities import find_prime
from workflows.prime_workflow import FindPrimeFlow
from temporalClient import TemporalClient
from config import logger as log
from config import settings as config
import uuid

async def invokePrimeWorkflow(number: int) -> str :
    log.info(f"invokePrimeWorkflow {number}")

    client = await TemporalClient.get_instance()

    result = await client.execute_workflow(
        FindPrimeFlow.run, number, id=("PrimeWorkflow_"+str(uuid.uuid4())), task_queue=config.temporal_queue_name
    )

    return result