from typing import Dict
from Models.Base import Process
from Models.GlobalParams import Global_params
from config import api_credentials
from config import logger as log

import json

from Clients.SSHClient import SSHClient

from temporalio import activity

class CliStep(Process):
    """This class will execute a list of commands on a remote host through SSH"""
    def __init__(self, config):
        super().__init__(config)
        self.commands = self.config['config']
        self.hostname = self.config['hostname']
        self.payload = self.render_jinja_template()
    def render_jinja_template(self):
        return self.commands
    def validate_process(self, output: str):
        log.debug(f"CliStep validate_process output\n{output}")
    def process_step(self):
        log.debug(f"CliStep process payload\n{self.payload}")
        self.payload = self.replace_params(self.payload).splitlines()
        log.debug(f"CliStep process hostname: {self.hostname} - username: {self.username} - password: {self.password}")
        
        client = SSHClient(self.hostname, self.username, self.password)

        for command in self.payload:
            print(f"Command: {command}")
            output = client.execute_command(command)
            print(f"Output: {output}")

        client.close()
    def toJSON(self):
        return super().toJSON()

@activity.defn
async def exec_cli_step(conf: Dict) -> int:
    log.debug(f"CliStep exec_rest_step {conf}")
    step = CliStep(conf)
    result = step.process_step()
    log.debug(f"CliStep process_step {step} - {result}")
    return result