from Models.Base import Process
from config import api_credentials, Global_params
from config import logger as log

import requests
from typing import Optional, Union, Dict
from jsonpath_ng.ext import parser
import json

global_params = Global_params()

from temporalio import activity, workflow

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RestStep(Process):
    """This class will be used to execute REST API calls"""
    url: str = field(init=False)
    headers: Optional[Dict[str, str]] = field(init=False)
    method: str = field(init=False)
    response: Dict = field(init=False)
    payload: Optional[str] = field(init=False)

    def __init__(self, config: Dict):
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
                        expression = parser.parse(path)
                        result = [match.value for match in expression.find(response.json())]
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
                path = key
                expression = parser.parse(path)
                result = [match.value for match in expression.find(response.json())]
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
    def process_step(self) -> int:
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
        return 1
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)
    

@activity.defn
async def exec_rest_step(step: RestStep) -> int:
    workflow.log.debug(f"RestStep exec_rest_step {step}")
    log.debug(f"RestStep process_step {step}")