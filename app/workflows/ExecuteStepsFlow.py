
from temporalio import workflow
import json

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from datetime import timedelta
    from config import logger as log
    from Models.RestStep import RestStep, exec_rest_step
    from Models.CliStep import CliStep, exec_cli_step
    from Models.NetConfStep import NetConfStep, exec_netconf_step
    from Models.GrpcStep import GrpcStep, exec_grpc_step

@workflow.defn
class ExecuteRestTask:
    def __init__(self) -> None:
        workflow.logger.debug(f"ExecuteRestTask::__init__")
        self.step: RestStep = None
   
    @workflow.run
    async def run(self, step: RestStep) -> int:
        # self.step = step

        workflow.logger.debug(f"Executing step: {step}")
        result1 = await workflow.execute_activity(
            exec_rest_step, step, start_to_close_timeout=timedelta(seconds=15)
        )
        workflow.logger.info(f"ExecuteStepsFlow::run: {step}! = {result1}")
            