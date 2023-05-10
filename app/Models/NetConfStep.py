from typing import Dict
from Clients.NetConfClient import NetConfClient
from Models.Base import Process
from config import api_credentials, Global_params
from config import logger as log

import json
from jsonpath_ng.ext import parser
import xmltodict
import xml.etree.ElementTree as ET

global_params = Global_params()

from temporalio import activity

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

                    path = value
                    expression = parser.parse(path)
                    result = [match.value for match in expression.find(data)]

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
    @activity.defn
    def process_step(self) -> int:
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
        return 0
    
    def toJSON(self):
        return super().toJSON()

@activity.defn
async def exec_netconf_step(conf: Dict) -> int:
    log.debug(f"NetConfStep exec_rest_step {conf}")
    step = NetConfStep(conf)
    result = step.process_step()
    log.debug(f"NetConfStep process_step {step} - {result}")
    return result