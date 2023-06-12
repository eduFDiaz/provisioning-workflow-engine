import yaml

from Utils.Utils import read_step_yaml, get_list_of_steps


from config import logger as log
from config import workflow_definition_files_path as path
from config import settings

from typing import Tuple, Any, Optional, Dict
from collections import OrderedDict

from temporalClient import TemporalClient
from workflows.activities.activities import read_template, exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step

from config import workflow_definition_files_path as path

from Models.GlobalParams import Global_params
from Models.Base import TemplateWorkflowArgs

from datetime import timedelta

from temporalio.common import RetryPolicy
from temporalio import workflow
from temporalio.workflow import ParentClosePolicy

@workflow.defn
class TemplateWorkflow:
    def __init__(self) -> None:
        log.debug(f"__init__")
    @workflow.run
    async def run(self, args: TemplateWorkflowArgs) -> int:
        log.debug(f"workflow: {args.WorkflowFileName}, correlation-id: {args.requestId}")
        taskList = await workflow.execute_activity(
            read_template, args=[args.WorkflowFileName, args.requestId], start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        log.debug(f"taskList len = {len(taskList)}")
        results = [await RunTask(task) for task in taskList]
        return None

@workflow.defn
class TemplateChildWorkflow:
    def __init__(self) -> None:
        log.debug(f"__init__")
    @workflow.run
    async def run(self, task: Dict) -> int:
        steps = task.get('steps')
        log.debug(f"step count: {len(steps)}")
        results = [await run_step(step.get('config')) for step in steps]
        return None    

async def RunTask(task):
    taskType = task.get('type')
    log.debug(f"executing task {task.get('name')} of type {taskType}")
    if taskType == 'workflow':
        log.debug(f"starting child workflow {task.get('file')}")
        result = await workflow.execute_child_workflow(
            TemplateChildWorkflow.run, task, 
            id=(task.get('file') + "_" + task.get('correlationID')), 
            execution_timeout=timedelta(seconds=settings.temporal_workflow_execution_timeout),
            parent_close_policy= ParentClosePolicy.TERMINATE
        )
        
    #TODO: add code for starting activity
        
    return
      
async def run_step(stepConfig):
    """This function will create an API object based on the configType"""
    log.debug(f"stepConfig: {stepConfig}")
    step_type = stepConfig.get('configType')
    log.debug(f"Creating API object for configType: {step_type}")
    # client = (await TemporalClient.get_instance())
    if step_type == 'REST':
        result = await workflow.execute_activity(
            exec_rest_step, stepConfig, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'CLI':
        result = await workflow.execute_activity(
            exec_cli_step, stepConfig, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'NETCONF':
        result = await workflow.execute_activity(
            exec_netconf_step, stepConfig, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    elif step_type == 'GRPC':
        result = await workflow.execute_activity(
            exec_grpc_step, stepConfig, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        log.debug(f"Result: {result}")
        return (result, stepConfig['name'])
    else:
        log.error(f"Unsupported configType: {step_type}")
        raise ValueError(f"Unsupported configType: {step_type}")



async def get_steps_configs(file: str, correlationID: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"get_steps_configs")
    # milestonesResult will be a map of milestone names to a list of steps
    milestonesResult = OrderedDict()
    root_flow_path = f"{path}/{file}"
    dict = read_step_yaml(root_flow_path)

    global_params = Global_params().getMap(correlationID)
    values_data = read_step_yaml(root_flow_path.replace('.yml','.values.yml'))
    for key, value in values_data.items():
        global_params[key]=value

    # log global_params entries
    log.debug(f"global_params: {global_params}")
    
    for milestone in dict['steps']:
        steps, error = get_list_of_steps(milestone['file'], correlationID)
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
                    step['correlationID'] = correlationID
                # rename workflow_name to workflow to match notification schema
                step['workflow'] = step.pop('workflow_name')
                step['step'] = step.pop('name')
        milestonesResult[milestone['name']] = steps

    # log milestoneResult entries
    for key, value in milestonesResult.items():
        log.debug(f"key: {key}, value: {value}")

    return milestonesResult, None