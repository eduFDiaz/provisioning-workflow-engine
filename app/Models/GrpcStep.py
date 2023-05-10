from typing import Dict
from Models.Base import Process
from config import api_credentials, Global_params
from config import logger as log

import grpc, json

from temporalio import activity

class GrpcStep(Process):
    """This class will execute a list of commands on a remote host through gRPC"""
    def __init__(self, config):
        super().__init__(config)
    @activity.defn
    def process_step(self):
        log.debug("GrpcStep process")
        # TODO Implement gRPC process logic here
        # hostname = self.config['hostname']
        # port = self.config['port']

        # channel = grpc.insecure_channel(f"{hostname}:{port}")

        # # Create a stub object for your gRPC service, e.g.
        # # stub = my_grpc_module.MyServiceStub(channel)

        # # Call your gRPC methods using the stub object and implement your specific gRPC process logic here
        # # e.g. response = stub.MyMethod(request)
    def toJSON(self):
        return super().toJSON()

@activity.defn
async def exec_grpc_step(conf: Dict) -> int:
    log.debug(f"GrpcStep exec_rest_step {conf}")
    step = GrpcStep(conf)
    result = step.process_step()
    log.debug(f"GrpcStep process_step {step} - {result}")
    return result