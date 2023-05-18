import time
from temporalio import activity, workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from datetime import timedelta    
    from config import logger as log
    from typing import Dict
    from Models.RestStep import RestStep
    from Models.CliStep import CliStep
    from Models.NetConfStep import NetConfStep
    from Models.GrpcStep import GrpcStep

@activity.defn
async def exec_rest_step(conf: Dict) -> int:
    log.debug(f"RestStep exec_rest_step {conf}")
    step = RestStep(conf)
    result = step.process_step()
    log.debug(f"RestStep process_step {step} - {result}")
    return result

@activity.defn
async def exec_netconf_step(conf: Dict) -> int:
    log.debug(f"NetConfStep exec_rest_step {conf}")
    step = NetConfStep(conf)
    result = step.process_step()
    log.debug(f"NetConfStep process_step {step} - {result}")
    return result

@activity.defn
async def exec_cli_step(conf: Dict) -> int:
    log.debug(f"CliStep exec_rest_step {conf}")
    step = CliStep(conf)
    result = step.process_step()
    log.debug(f"CliStep process_step {step} - {result}")
    return result

@activity.defn
async def exec_grpc_step(conf: Dict) -> int:
    log.debug(f"GrpcStep exec_rest_step {conf}")
    step = GrpcStep(conf)
    result = step.process_step()
    log.debug(f"GrpcStep process_step {step} - {result}")
    return result