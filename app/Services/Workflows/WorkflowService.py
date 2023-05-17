from Models.Base import Process
from Models.RestStep import RestStep
from Models.CliStep import CliStep
from Models.GrpcStep import GrpcStep
from Models.NetConfStep import NetConfStep
from Utils.Utils import read_step_yaml, read_flow_yaml

from config import logger as log



from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from temporalClient import TemporalClient
from config import logger as log
from config import settings as config
import uuid

async def run_step(stepConfig):
    """This function will create an API object based on the configType"""
    step_type = stepConfig.get('configType')
    log.debug(f"Creating API object for configType: {step_type}")
    client = (await TemporalClient.get_instance())
    if step_type == 'REST':
        result = (await client.execute_workflow(
            ExecuteRestTask.run, stepConfig, id=("ExecuteRestTask_"+stepConfig['name']), task_queue=config.temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'CLI':
        result = (await client.execute_workflow(
            ExecuteCliTask.run, stepConfig, id=("ExecuteCliTask_"+stepConfig['name']), task_queue=config.temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'NETCONF':
        result = (await client.execute_workflow(
            ExecuteNetConfTask.run, stepConfig, id=("ExecuteNetConfTask_"+stepConfig['name']), task_queue=config.temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'GRPC':
        result = (await client.execute_workflow(
            ExecuteGrpcTask.run, stepConfig, id=("ExecuteGrpcTask_"+stepConfig['name']), task_queue=config.temporal_queue_name
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    else:
        log.error(f"Unsupported configType: {step_type}")
        raise ValueError(f"Unsupported configType: {step_type}")

async def invoke_steps(file: str) -> int:
    log.debug(f"Invoking steps")
    
    flow_data = read_flow_yaml(f"./Worflows_Definition_Files/{file}")
    results = [await run_step(read_step_yaml(f"./Worflows_Definition_Files/{config['file']}")) for config in flow_data['steps']]
    return results

    