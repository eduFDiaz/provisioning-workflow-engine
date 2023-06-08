from Utils.Utils import read_step_yaml, get_list_of_steps

from config import logger as log
from config import workflow_definition_files_path as path
# from config import temporal_queue_name
from config import configs

from typing import Tuple, Any, Optional
from collections import OrderedDict

from temporalClient import TemporalClient
from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask

from config import workflow_definition_files_path as path
from Models.GlobalParams import Global_params

global_params = Global_params()

async def run_step(stepConfig):
    """This function will create an API object based on the configType"""
    step_type = stepConfig.get('configType')
    log.debug(f"Creating API object for configType: {step_type}")
    client = (await TemporalClient.get_instance())
    if step_type == 'REST':
        result = (await client.execute_workflow(
            ExecuteRestTask.run, stepConfig, id=("ExecuteRestTask_"+stepConfig['name']), task_queue=configs.get("temporal.queuename").data
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'CLI':
        result = (await client.execute_workflow(
            ExecuteCliTask.run, stepConfig, id=("ExecuteCliTask_"+stepConfig['name']), task_queue=configs.get("temporal.queuename").data
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'NETCONF':
        result = (await client.execute_workflow(
            ExecuteNetConfTask.run, stepConfig, id=("ExecuteNetConfTask_"+stepConfig['name']), task_queue=configs.get("temporal.queuename").data
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'GRPC':
        result = (await client.execute_workflow(
            ExecuteGrpcTask.run, stepConfig, id=("ExecuteGrpcTask_"+stepConfig['name']), task_queue=configs.get("temporal.queuename").data
        ))
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    else:
        log.error(f"Unsupported configType: {step_type}")
        raise ValueError(f"Unsupported configType: {step_type}")

async def invoke_steps(file: str, requestId: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"Invoking steps. requestId = {requestId} ")
    
    steps, error = await get_list_of_steps(file)
    
    if error:
        log.error(f"Error getting list of steps")
        return None, error
    
    results = [await run_step(stepConfig) for stepConfig in steps]
    return results

async def get_steps_configs(file: str, correlationId: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"get_steps_configs")

    # milestonesResult will be a map of milestone names to a list of steps
    milestonesResult = OrderedDict()
    root_flow_path = f"{path}/{file}"
    dict = read_step_yaml(root_flow_path)

    values_data = read_step_yaml(root_flow_path.replace('.yml','.values.yml'))
    for key, value in values_data.items():
        global_params.setitem(key, value)

    log.debug(f"Global params:\n{global_params.getMap()}")
    
    for milestone in dict['steps']:
        steps, error = await get_list_of_steps(milestone['file'])
        if error:
            log.error(f"Error getting list of steps")
            return None, error
    
        # we only want to return a subset of the keys from the configs, this may change in the future
        keys_to_keep = ['name', 'description', 'milestoneStepName', 'milestoneName', 'configType', 'workflow_name']

        if steps is not None:
            for step in steps:
                for key in list(step.keys()):
                    if key not in keys_to_keep:
                        del step[key]
                    #we will also add date properties to the step
                    step['startedDate'] = ""
                    step['endTime'] = ""
                    step['status'] = "not-started"
                    step['correlationId'] = correlationId
                # rename workflow_name to workflow to match notification schema
                step['workflow'] = step.pop('workflow_name')
                step['step'] = step.pop('name')
        milestonesResult[milestone['name']] = steps

    # log milestoneResult entries
    for key, value in milestonesResult.items():
        log.debug(f"key: {key}, value: {value}")

    return milestonesResult, None