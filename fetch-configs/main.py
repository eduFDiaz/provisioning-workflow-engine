import collections

# from NornirClient import NornirClient
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get

from NetConfClient import NetConfClient

from SSHClient import SSHClient
import yaml
import requests

import grpc
from config import api_credentials, Global_params
from jinja2 import Environment, Template, FileSystemLoader
from typing import Optional, Union

import json
from jsonpath import JSONPath

import xml.etree.ElementTree as ET
import xmltodict

import logging
FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='CONFIGS.log', filemode='a')

log = logging.getLogger()

global_params = Global_params()

class Process:
    """Base class for all process types"""
    def __init__(self, config):
        self.name = config['name']
        self.configType = config['configType']
        self.config = config
        self.set_credentials()
        self.templateParams = read_yaml(api_credentials[self.configType]['paramsFile'])
        global_params.update(self.templateParams)
    def process_step(self):
        """This method will be implemented by the child Step classes
        It will be used to execute the process, REST, CLI, NETCONF, etc"""
        raise NotImplementedError
    def validate_process(self):
        """This method will be implemented by the child classes"""
        raise NotImplementedError
    def render_jinja_template(self):
        """This method will be implemented by the child classes"""
        raise NotImplementedError
    def set_credentials(self):
        if self.configType not in api_credentials:
            log.error(f"Unsupported configType: {self.configType}")
            raise ValueError(f"Unsupported configType: {self.configType}")
        self.username = api_credentials[self.configType]['username']
        self.password = api_credentials[self.configType]['password']
    def replace_params(self, param: Union[str, dict]) -> Union[str, dict]:
        """ This method will replace all the jinja2 template variables with the values from the params file
        it will also replace header placeholders with the values from the global_params dictionary"""
        log.debug(f"template params -> global {global_params}")
        log.debug(f"{self.configType} before replace_params\n{param} - type: {type(param)}")
        if isinstance(param, str):
            template = Template(param, trim_blocks=True, lstrip_blocks=True)
            renderedParam = template.render(**global_params.getMap())
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        elif isinstance(param, dict):
            renderedParam = {}
            for key, value in param.items():
                renderedParam[key] = self.replace_params(value)
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        raise ValueError(f"Unsupported type: {type(param)}")

class RestStep(Process):
    """This class will be used to execute REST API calls"""
    def __init__(self, config):
        super().__init__(config)
        self.url = self.config['request']['url']
        self.headers = self.config['request'].get('headers')
        self.method = self.config['request']['method']
        if self.method not in ['GET', 'POST']:
            raise ValueError(f"Unsupported HTTP method: {self.method}")
        self.response = self.config['response']
        self.payload = self.render_jinja_template()
    def render_jinja_template(self) -> Optional[str]:
        """This method will render the jinja2 template for the payload"""
        log.debug("RestStep render_jinja_template")
        payload = self.config['request'].get('payload')
        if self.method == 'POST' and payload is not None:
            self.payload = self.replace_params(payload)
            return self.payload
        else:
            return None
    def extract_variables(self, response: requests.Response) -> bool:
        """This method will extract variables from the response payload/headers and store them in the global_params dictionary"""
        log.debug(f"RestStep extract_variables response\n{response}")
        if self.response is not None and self.response.get('variables') is not None:
            for key, value in self.response['variables'].items():
                log.debug(f"RestStep extract_variables key: {key} value: {value}")
                try:
                    if "json." in value:
                        path = value.replace("json.", "")
                        result = JSONPath(value.replace("json.", "")).parse(response.json())
                        log.debug(f"RestStep extract_variables json result: {result} - path: {path} - key: {key}")
                    if "header." in value:
                        result = response.headers.get(value.replace("header.", ""))
                    if result is None or len(result) == 0:
                        raise ValueError(f"Error extracting variable: {key} - {value}")
                    global_params.setitem(key, result)
                except Exception as e:
                        log.error(f"RestStep extract_variables error: {e}")
                        return False
        else:
            return True
        return True
    def validate_process(self, response: requests.Response):
        """This method will validate the response from the REST API call
        1. It will validate the status code
        2. It will validate attributes of response
        3. It will extract variables from the response payload/headers and store them in the global_params dictionary
           throwing an exception if the variable is not found
        """
        log.debug(f"RestStep validate_process response\n{response}")
        if self.response is not None and self.response.get('status_code') is not None:
            if response.status_code != self.response['status_code']:
                raise ValueError(f"Status code mismatch: {response.status_code} != {self.response['status_code']}")
        if self.response is not None and self.response.get('json') is not None: 
            for key, value in self.response['json'].items():
                log.debug(f"RestStep validate_process json key: {key} value: {value}")
                # Define a JSONPath query
                result = JSONPath(key).parse(response.json())
                log.debug(f"RestStep validate_process json result: {result}")
                if result != global_params.getitem(value):
                    raise ValueError(f"JSON key mismatch: {key} != {global_params.getitem(value)}")
                log.debug(f"RestStep validate_process json result: {result} - {value} - {global_params.getitem(value)}")
        if self.extract_variables(response) == False:
            raise ValueError(f"Error extracting variables")
    def prepare_step(self):
        """This method will prepare the request, adding headers and replacing url and payload params"""
        log.debug(f"RestStep prepare_request")
        self.url = self.replace_params(self.url)
        self.headers = self.replace_params(self.headers)
        if self.method == 'POST':
            self.payload = self.replace_params(self.payload)
    def process_step(self):
        """This method will execute the REST API call"""
        self.prepare_step()
        if self.method == 'GET':
            log.debug(f"RestStep process GET {self.url}")
            log.debug(f"RestStep process GET payload: {self.payload}")
            log.debug(f"RestStep process GET headers: {self.headers}")
            # # mock response for development
            # response = requests.Response()
            # response.status_code = 200
            # response.headers['Server'] = 'nginx/1.13.12'
            # response._content = b"""
            # {}
            # """
            response = requests.get(self.url, auth=(self.username, self.password), headers=self.headers, verify=False)
            #log pretty print json response
            log.debug(f"RestStep process GET response\n{json.dumps(response.json(), indent=4)}")
        elif self.method == 'POST':
            log.debug(f"RestStep process POST {self.url}")
            log.debug(f"RestStep process POST payload: {self.payload}")
            # global param token was made available after the 1rst API Step
            self.headers['X-CSRF-Token']='{{token}}'
            self.headers = self.replace_params(self.headers)
            # response = requests.post(self.url, auth=(self.username, self.password), json=self.payload, headers=self.headers, verify=False)
            # mock response for development
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"status": "success"}'
        self.validate_process(response)
        log.debug(f"{self.name} - {self.method} {self.url} - {response.content} - Status code: {response.status_code}")
        
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

class NetConfStep(Process):
    """This class will execute a list of commands on a remote host through NETCONF"""
    def __init__(self, config):
        super().__init__(config)
        self.hostname = self.config['hostname']
        self.port = self.config['port']
        self.username = api_credentials[self.configType]['username']
        self.password = api_credentials[self.configType]['password']
        self.request = self.config['request']
        if self.request['type'] not in ['FETCH', 'EDIT']:
            raise ValueError(f"Invalid request type: {self.request['type']}")
        self.type = self.request['type']
    def render_jinja_template(self):
        log.debug("netconfStep render_jinja_template")
        payload = self.request['payload']
        return self.replace_params(payload)
    def validate_process(self, output: str) -> bool:
        log.debug(f"NetConfStep validate_process output\n{output}")
        
        # Parse the XML data
        root = ET.fromstring(output)
        
        # Find the 'ok' element using an XPath expression
        ok_element = root.find("./ok")

        # Check if the 'ok' element exists
        if ok_element is not None:
            return True
        else:
            return False
    def extract_variables(self, response: str) -> bool:
        """This method will extract variables from the response payload/headers and store them in the global_params dictionary"""
        log.debug(f"RestStep extract_variables response\n{response}")
        if self.request is not None and self.request.get('variables') is not None:
            for key, value in self.request['variables'].items():
                try:
                    log.debug(f"RestStep extract_variables key: {key} value: {value}")
                    # Convert XML to JSON
                    data_dict = xmltodict.parse(response)
                    json_data = json.dumps(data_dict)

                    # Load the JSON data as a Python dictionary
                    data = json.loads(json_data)

                    result = JSONPath(value).parse(data)

                    if len(result) == 0:
                        raise ValueError(f"No matching value for {value}")

                    if len(result) == 1:
                        result = result[0]

                    log.debug(f"RestStep extract_variables result: {result}")
                    
                    global_params.setitem(key, result)
                    log.debug(f"RestStep extract_variables global_params: {global_params}")
                except Exception as e:
                        log.error(f"RestStep extract_variables error: {e}")
                        return False
        else:
            return True
        return True
    def validate_process(self, output: str):
        log.debug(f"NetConfStep validate_process output\n{output}")
        # TODO Implement NETCONF validation logic here
    def process_step(self):
        log.debug("NetConfStep process")
        self.payload = self.render_jinja_template()
        
        config = {
            "host": self.hostname,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "port": self.port,
        }

        client = NetConfClient(config)

        if self.type == 'FETCH':
            result = client.get_filter(self.payload)
            self.extract_variables(result)
        elif self.type == 'EDIT':
            result = client.edit_config(self.payload)
            self.validate_process(result)

        log.debug(f"NetConfStep process result\n{result}")


class GrpcStep(Process):
    """This class will execute a list of commands on a remote host through gRPC"""
    def __init__(self, config):
        super().__init__(config)
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

def read_yaml(file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    log.debug(f"Reading YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def create_api_object(config):
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
    
if __name__ == "__main__":
    yaml_data = read_yaml("./phy_interface_vlan.yml")
    steps = [create_api_object(config) for config in yaml_data['steps']]

    for step in steps:
        log.debug(f"Processing {step.name} - {step.configType} - {step.username} - {step.password}")
        step.process_step()