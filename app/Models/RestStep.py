from Models.Base import Process
from Models.Errors.CustomRestStepError import CustomRestStepError, REST_ERRORS
from config import logger as log

import requests
from typing import Optional
from jsonpath_ng.ext import parser
import json
from urllib.parse import urlparse

class RestStep(Process):
    """This class will be used to execute REST API calls"""
    def __init__(self, config):
        super().__init__(config)
        self.url = self.config['request']['url']
        self.headers = self.config['request'].get('headers')
        self.method = self.config['request']['method']
        if self.method not in ['GET', 'POST']:
            raise ValueError(CustomRestStepError(REST_ERRORS.UNSUPPORTED_METHOD, args={ 'method' : self.method }).toJSON())
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
                        raise ValueError(CustomRestStepError(REST_ERRORS.EXTRACT_VALUE_ERROR, args={ 'path' : value }).toJSON())
                    self.global_params[key] = result
                except Exception as e:
                        log.error(f"RestStep extract_variables error: {e}")
                        return False
            log.debug(f"RestStep global_params after extracting variables from the response: {self.global_params}")
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
                raise ValueError(CustomRestStepError(payload=REST_ERRORS.STATUS_CODE_MISMATCH, args={'actualStatusCode' : response.status_code, 'expectedStatusCode' : self.response['status_code']}).toJSON())
        if self.response is not None and self.response.get('json') is not None: 
            for key, value in self.response['json'].items():
                log.debug(f"RestStep validate_process json key: {key} value: {value}")
                # Define a JSONPath query
                path = key
                expression = parser.parse(path)
                result = [match.value for match in expression.find(response.json())]
                log.debug(f"RestStep validate_process json result: {result}")
                if result != self.global_params[value]:
                    raise ValueError(CustomRestStepError(payload=REST_ERRORS.PARAM_VALUE_MISMATCH, args={'path' : key, 'expectedValue' : self.global_params[value]}).toJSON())
                log.debug(f"RestStep validate_process json result: {result} - {value} - {self.global_params[value]}")
        if self.extract_variables(response) == False:
            raise ValueError(CustomRestStepError(payload=REST_ERRORS.EXTRACT_VALUE_UNHANDLED_ERROR, args={}).toJSON())
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
        try:
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
                self.headers = self.replace_params(self.headers)
                response = requests.post(self.url, auth=(self.username, self.password), json=self.payload, headers=self.headers, verify=False)
                # # mock response for development
                # response = requests.Response()
                # response.status_code = 200
                # response._content = b'{"status": "success"}'
        except Exception as e:
            raise ValueError(CustomRestStepError(payload=e, args={'host': urlparse(self.url).hostname, 'port': urlparse(self.url).port, 'url': self.url, 'auth': (self.username, self.password), 'headers': self.headers, 'payload': self.payload}).toJSON())
        self.validate_process(response)
        log.debug(f"{self.name} - {self.method} {self.url} - {response.content} - Status code: {response.status_code}")
        return 1000

