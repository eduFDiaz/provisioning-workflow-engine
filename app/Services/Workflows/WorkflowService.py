from Utils.Utils import read_step_yaml, get_list_of_steps

from config import logger as log
from config import workflow_definition_files_path as path
from config import temporal_queue_name

from typing import Tuple, Any, Optional

from temporalClient import TemporalClient
from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask


async def run_step(stepConfig):
    """This function will create an API object based on the configType"""
    step_type = stepConfig.get('configType')
    log.debug(f"Creating API object for configType: {step_type}")
    client = (await TemporalClient.get_instance())
    if step_type == 'REST':
        result = (await client.execute_workflow(
            ExecuteRestTask.run, stepConfig, id=("ExecuteRestTask_"+stepConfig['name']), task_queue=temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'CLI':
        result = (await client.execute_workflow(
            ExecuteCliTask.run, stepConfig, id=("ExecuteCliTask_"+stepConfig['name']), task_queue=temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'NETCONF':
        result = (await client.execute_workflow(
            ExecuteNetConfTask.run, stepConfig, id=("ExecuteNetConfTask_"+stepConfig['name']), task_queue=temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'GRPC':
        result = (await client.execute_workflow(
            ExecuteGrpcTask.run, stepConfig, id=("ExecuteGrpcTask_"+stepConfig['name']), task_queue=temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    else:
        log.error(f"Unsupported configType: {step_type}")
        raise ValueError(f"Unsupported configType: {step_type}")

async def invoke_steps(file: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"Invoking steps")
    
    steps, error = await get_list_of_steps(file)
    
    if error:
        log.error(f"Error getting list of steps")
        return None, error
    
    results = [await run_step(stepConfig) for stepConfig in steps]
    return results