import collections
import yaml
import requests
import paramiko
from ncclient import manager
import grpc
from config import api_credentials, global_params
from jinja2 import Environment, Template, FileSystemLoader
from typing import Optional

import json
from jsonpath import JSONPath

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT) #filename="log.txt"
# Creating a logger object
log = logging.getLogger()

class Process:
    def __init__(self, config):
        self.name = config['name']
        self.configType = config['configType']
        self.config = config
        self.set_credentials()
        self.templateParams = read_yaml(api_credentials[self.configType]['paramsFile'])
        global_params.update(self.templateParams)
    def process(self):
        raise NotImplementedError
    def validate_process(self):
        raise NotImplementedError
    def render_jinja_template(self):
        raise NotImplementedError
    def set_credentials(self):
        if self.configType not in api_credentials:
            log.error(f"Unsupported configType: {self.configType}")
            raise ValueError(f"Unsupported configType: {self.configType}")
        self.username = api_credentials[self.configType]['username']
        self.password = api_credentials[self.configType]['password']
    def replace_params(self, param: str) -> str:
        log.debug(f"template params -> global {global_params}")
        log.debug(f"{self.configType} before replace_params\n{param}")
        template = Template(param, trim_blocks=True, lstrip_blocks=True)
        renderedParam = template.render(**global_params)
        log.debug(f"{self.configType} after replace_params\n{renderedParam}")
        return renderedParam

class RestStep(Process):
    def __init__(self, config):
        super().__init__(config)
        self.url = self.config['request']['url']
        self.headers = {'Content-Type': 'application/json'}
        self.method = self.config['request']['method']
        if self.method not in ['GET', 'POST']:
            raise ValueError(f"Unsupported HTTP method: {self.method}")
        self.response = self.config['response']
        self.payload = self.render_jinja_template()
    def render_jinja_template(self) -> Optional[str]:
        log.debug("RestStep render_jinja_template")
        payload = self.config['request'].get('payload')
        if self.method == 'POST' and payload is not None:
            self.payload = self.replace_params(payload)
            return self.payload
        else:
            return None
    def extract_variables(self, response: requests.Response) -> bool:
        log.debug(f"RestStep extract_variables response\n{response}")
        if self.response is not None and self.response.get('variables') is not None:
            for key, value in self.response['variables'].items():
                log.debug(f"RestStep extract_variables key: {key} value: {value}")
                try:
                    if "json." in value:
                        result = JSONPath(key.replace("json.", "")).parse(response.json())
                        global_params[key] = result
                    if "header." in value:
                        result = response.headers.get(value.replace("header.", ""))
                        log.debug(f"RestStep extract_variables headera result: {result}")
                        global_params[key] = result
                except Exception as e:
                        log.error(f"RestStep extract_variables error: {e}")
                        return False
        else:
            return True
        return True
    def validate_process(self, response: requests.Response):
        log.debug(f"RestStep validate_process response\n{response}")
        if self.response is not None and self.response.get('status_code') is not None:
            if response.status_code != self.response['status_code']:
                raise ValueError(f"Status code mismatch: {response.status_code} != {self.response['status_code']}")
        if self.response is not None and self.response.get('json') is not None: 
            for key, value in self.response['json'].items():
                log.debug(f"RestStep validate_process json key: {key} value: {value}")
                # Define a JSONPath query
                result = JSONPath(key).parse(response.json())
                if result != global_params.get(value):
                    raise ValueError(f"JSON key mismatch: {key} != {global_params.get(value)}")
                log.debug(f"RestStep validate_process json result: {result} - {value} - {global_params.get(value)}")
        if self.extract_variables(response) == False:
            raise ValueError(f"Error extracting variables")
    def process(self):
        self.url = self.replace_params(self.url)
        if self.method == 'GET':
            log.debug(f"RestStep process GET {self.url}")
            log.debug(f"RestStep process GET payload: {self.payload}")
            # response = requests.get(self.url, auth=(self.username, self.password), headers=self.headers)
            # mock response for development
            response = requests.Response()
            response.status_code = 200
            response.headers['X-CSRF-Token'] = '3a78ddff-415c-4077-971d-63b770f5ec7c'
            response._content = b"""
            {
                "city_id": "AUSTIN",
                "state_id": "TX",
                "sites": [ 
                    {"name" : "site1"},
                    {"name" : "site2"}
                ]
            }
            """
            self.validate_process(response)
            log.debug(f"{self.name} - {self.method} {self.url} - {response.content} - Status code: {response.status_code}")
            log.debug(f"{response.content} - Status code: {response.status_code}")
        elif self.method == 'POST':
            log.debug(f"RestStep process POST {self.url}")
            log.debug(f"RestStep process POST payload: {self.payload}")
            # response = requests.post(self.url, auth=(self.username, self.password), json=self.payload, headers=self.headers)
            # mock response for development
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"status": "success"}'
            self.validate_process(response)
            log.debug(f"{self.name} - {self.method} {self.url} - {response.content} - Status code: {response.status_code}")
        
        # log.debug(f"{self.name} - {self.method} {self.url} - Status code: {response.status_code}")

class CliStep(Process):
    def __init__(self, config):
        super().__init__(config)
        self.commands = self.config['config']
        self.payload = self.render_jinja_template()
    def render_jinja_template(self):
        return self.commands
    def validate_process(self, output: str):
        log.debug(f"CliStep validate_process output\n{output}")
        pass
    def process(self):
        log.debug(f"CliStep process payload\n{self.payload}")
        self.payload = self.replace_params(self.payload)
        # hostname = self.config['hostname']
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(hostname, username=self.username, password=self.password)

        # for command in self.commands:
        #     stdin, stdout, stderr = ssh.exec_command(command)
        #     log.debug(f"{self.name} - Executed command: {command}")
        #     log.debug(stdout.read().decode())

        # ssh.close()

class NetConfStep(Process):
    def __init__(self, config):
        super().__init__(config)
        self.payload = self.render_jinja_template()
    def render_jinja_template(self):
        # TODO Implement Jinja template rendering logic here
        log.debug("netconfStep render_jinja_template")
        pass
    def validate_process(self, output: str):
        log.debug(f"NetConfStep validate_process output\n{output}")
        pass
    def process(self):
        log.debug("NetConfStep process")
        # hostname = self.config['hostname']
        # port = self.config['port']

        # with manager.connect(
        #     host=hostname,
        #     port=port,
        #     username=self.username,
        #     password=self.password,
        #     hostkey_verify=False,
        #     device_params={'name': 'default'}
        # ) as m:
        #     # TODO Implement NETCONF process logic here
        #     pass

class GrpcStep(Process):
    def __init__(self, config):
        super().__init__(config)
    def process(self):
        log.debug("GrpcStep process")
        # hostname = self.config['hostname']
        # port = self.config['port']

        # channel = grpc.insecure_channel(f"{hostname}:{port}")

        # # Create a stub object for your gRPC service, e.g.
        # # stub = my_grpc_module.MyServiceStub(channel)

        # # Call your gRPC methods using the stub object and implement your specific gRPC process logic here
        # # e.g. response = stub.MyMethod(request)

def read_yaml(file_path) -> collections.OrderedDict:
    log.debug(f"Reading YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def create_api_object(config):
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
    
if __name__ == "__main__":
    yaml_data = read_yaml("./phy_interface_activation.yml")
    steps = [create_api_object(config) for config in yaml_data['steps']]

    for step in steps:
        log.debug(f"Processing {step.name} - {step.configType} - {step.username} - {step.password}")
        step.process()