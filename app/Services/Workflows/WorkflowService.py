from Models.Base import Process
from Models.RestStep import RestStep
from Models.CliStep import CliStep
from Models.GrpcStep import GrpcStep
from Models.NetConfStep import NetConfStep
from Utils.Utils import read_yaml

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

async def invoke_steps() -> int:
    log.debug(f"Invoking steps")

    yaml_data = read_yaml("./phy_interface_vlan.yml")
    results = [await run_step(config) for config in yaml_data['steps']]

    return results

    