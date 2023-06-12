
from temporalio import workflow
from temporalio.common import RetryPolicy
from config import logger as log, settings


# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from datetime import timedelta    
    from typing import Dict
    from workflows.activities.activities import exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step
    
@workflow.defn
class ExecuteRestTask:
    def __init__(self) -> None:
        workflow.logger.debug(f"ExecuteRestTask::__init__")
    @workflow.run
    async def run(self, conf: Dict) -> int:
        workflow.logger.debug(f"Executing step: {conf['name']} - {conf['configType']}")
        result = await workflow.execute_activity(
            exec_rest_step, conf, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        return result

@workflow.defn
class ExecuteCliTask:
    def __init__(self) -> None:
        workflow.logger.debug(f"ExecuteCliTask::__init__")
    @workflow.run
    async def run(self, conf: Dict) -> int:
        workflow.logger.debug(f"Executing step: {conf['name']} - {conf['configType']}")
        result = await workflow.execute_activity(
            exec_cli_step, conf, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        return result

@workflow.defn
class ExecuteNetConfTask:
    def __init__(self) -> None:
        workflow.logger.debug(f"ExecuteNetConfTask::__init__")
    @workflow.run
    async def run(self, conf: Dict) -> int:
        workflow.logger.debug(f"Executing step: {conf['name']} - {conf['configType']}")
        result = await workflow.execute_activity(
            exec_netconf_step, conf, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        return result

@workflow.defn
class ExecuteGrpcTask:
    def __init__(self) -> None:
        workflow.logger.debug(f"ExecuteGrpcTask::__init__")
    @workflow.run
    async def run(self, conf: Dict) -> int:
        workflow.logger.debug(f"Executing step: {conf['name']} - {conf['configType']}")
        result = await workflow.execute_activity(
            exec_grpc_step, conf, start_to_close_timeout=timedelta(seconds=settings.temporal_task_start_to_close_timeout),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=settings.temporal_task_init_interval),
                backoff_coefficient=settings.temporal_task_backoff_coefficient,
                maximum_attempts=settings.temporal_task_max_attempts,
                maximum_interval=timedelta(seconds=settings.temporal_task_max_interval))
        )
        return result

