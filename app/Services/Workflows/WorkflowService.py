from Models.Base import Process
from Models.RestStep import RestStep
from Models.CliStep import CliStep
from Models.GrpcStep import GrpcStep
from Models.NetConfStep import NetConfStep
from Utils.Utils import read_yaml

from config import logger as log



from workflows.ExecuteStepsFlow import ExecuteRestTask
from temporalClient import TemporalClient
from config import logger as log
from config import settings as config
import uuid

import json

def create_step_object(config):
    """This function will create an API object based on the configType"""
    step_type = config.get('configType')
    log.debug(f"Creating API object for configType: {step_type}")
    if step_type == 'REST':
        return RestStep(config)
    elif step_type == 'CLI':
        return CliStep(config)
    elif step_type == 'NETCONF':
        return NetConfStep(config)
    elif step_type == 'GRPC':
        return GrpcStep(config)
    else:
        log.error(f"Unsupported configType: {step_type}")
        raise ValueError(f"Unsupported configType: {step_type}")

async def invoke_steps() -> int:
    # for step in steps:
    #     log.debug(f"Processing {step.name} - {step.configType} - {step.username} - {step.password}")
    #     step.process_step()
    log.debug(f"Invoking steps")

    client = await TemporalClient.get_instance()

    yaml_data = read_yaml("./phy_interface_vlan.yml")
    steps = [create_step_object(config) for config in yaml_data['steps']]

    for step in steps:
        log.debug(f"Processing {step}")

        if step.configType == 'REST':
            log.debug(f"Invoking REST step")
            result = await client.execute_workflow(
                ExecuteRestTask.run, step, id=("ExecuteRestTask_"+str(uuid.uuid4())), task_queue=config.temporal_queue_name
            )
            log.debug(f"Result: {result}")
            return result

    