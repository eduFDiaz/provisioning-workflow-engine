
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
    async def run(self, step: str) -> int:
        self.step = json.loads(step)
        workflow.logger.debug(f"Executing step: {self.step}")
        result1 = await workflow.execute_activity(
            exec_rest_step, self.step, start_to_close_timeout=timedelta(seconds=15)
        )
        workflow.logger.info(f"ExecuteStepsFlow::run: {self.step}! = {result1}")
            