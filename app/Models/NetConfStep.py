from typing import Dict
from Clients.NetConfClient import NetConfClient
from Models.Base import Process
from config import logger as log
# from config import api_credentials

import json
from jsonpath_ng.ext import parser
import xmltodict

from typing import Dict
from Models.Errors.CustomNetconfStepError import CustomNetconfError, NETCONF_ERRORS

class NetConfStep(Process):
    """This class will execute a list of commands on a remote host through NETCONF"""
    def __init__(self, config):
        super().__init__(config)
        self.hostname = self.config['hostname']
        self.port = self.config['port']
        # self.username = api_credentials[self.configType]['username']
        # self.password = api_credentials[self.configType]['password']
        self.request = self.config['request']
        if self.request['type'] not in ['FETCH', 'EDIT']:
            raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.UNSUPPORTED_REQUEST_TYPE, args={'request_type': self.request['type']}).toJSON())
        self.type = self.request['type']
    def render_jinja_template(self):
        log.debug("netconfStep render_jinja_template")
        payload = self.request['payload']
        return self.replace_params(payload)
    def validate_fetch_response(self, output_json) -> bool:
        """This method will validate attributes of the FETCH response against global_params"""
        log.debug(f"NetConfStep validate_fetch_response output_json\n{output_json}")

        data = json.loads(output_json)
        log.debug(f"NetConfStep validate_fetch_response data: {json.dumps(data, indent=4, sort_keys=True)}")  
        
        if self.request is not None and self.request.get('validate') is not None:
            for key, value in self.request['validate'].items():
                log.debug(f"NetConfStep validate_fetch_response key: {key} value: {value}")
                
                try:
                    param = self.global_params[value]
                    log.debug(f"NetConfStep validate_fetch_response param: {param}")
                    
                    if param is None:
                        log.error(f"NetConfStep validate_fetch_response error: param {value} not found in global_params")
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_NOT_INITIALIZED, args={'param': value}).toJSON())
                    
                    path = key
                    expression = parser.parse(path)
                    
                    log.debug(f"expression: {expression}")
                    result = [match.value for match in expression.find(data)]
                    
                    if result is None or len(result) == 0:
                        log.error(f"NetConfStep validate_fetch_response error: {path} not found in response")
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_PATH_NOT_FOUND, args={'path': path}).toJSON())
                    if (param != result[0]):
                        log.error(f"NetConfStep validate_fetch_response error: {param} != {result[0]}") 
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_NOT_EQUAL, args={'param': param, 'result': result[0]}).toJSON())
                except Exception as e:
                        log.error(f"NetConfStep validate_fetch_response Exception: {e}")
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_EXCEPTION, args={'exception': e}).toJSON())
        
        log.info("Code reached end of validate_fetch_response, no params to validate or all params validated successfully")
        return True
    def validate_edit_response(self, output_dic: Dict) -> bool:
        """This method will validate the netconf edit response"""
        log.debug(f"NetConfStep validate_edit_response output_dic\n{output_dic}")
        try:
            if output_dic.get('rpc-reply').get('rpc-error') == None:
                log.info("NetConfStep response is </ok>")
                return True
        except KeyError as e:
            log.error(f"NetConfStep validate_process error: response was not </ok>: KeyError {e}")
            raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_EDIT_RESPONSE_ERROR, args={'response', xmltodict.unparse(output_dic)}).toJSON())
    def validate_process(self, output: str) -> bool:
        """This method will validate the netconf response for FETCH and EDIT requests"""
        log.debug(f"NetConfStep validate_process output\n{output}")
        output_dic = xmltodict.parse(output)
        output_json = json.dumps(output_dic)

        if self.request['type'] == 'EDIT':
            return self.validate_edit_response(output_dic)

        if self.request['type'] == 'FETCH':
            # Check if the response is empty
            if (output_dic.get('rpc-reply') != None and 
                    output_dic.get('rpc-reply').get('data') == None):
                log.error("NetConfStep validate_process error: response is empty")
                raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_EMPTY, args={'response', xmltodict.unparse(output_dic)}).toJSON())
            else:
                # proceed to validate attributes in the response
                return self.validate_fetch_response(output_json)

    def extract_variables(self, response: str) -> bool:
        """This method will extract variables from the response payload/headers and store them in the global_params dictionary
        this method will be only called if the validation of the response objects against global_params was successful"""
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
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.EXTRACT_VARIABLES_NO_MATCHING_VALUE, args={'path': value, 'response': data_dict}).toJSON())

                    if len(result) == 1:
                        result = result[0]

                    log.debug(f"RestStep extract_variables result: {result}")
                    
                    self.global_params[key] = result
                    log.debug(f"RestStep extract_variables global_params: {self.global_params}")
                except Exception as e:
                        log.error(f"RestStep extract_variables error: {e}")
                        raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.EXTRACT_VARIABLES_EXCEPTION, args={'exception': e}).toJSON())
        else:
            return True
        return True
    def process_step(self) -> int:
        log.debug("NetConfStep process")
        self.payload = self.render_jinja_template()
        self.hostname = self.replace_params(self.hostname)
        self.port = self.replace_params(self.port)
        
        config = {
            "host": self.hostname,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "port": int(self.port),
        }

        client = NetConfClient(config)

        if self.type == 'FETCH':
            result = client.get_filter(self.payload)            
            
            validProcess = self.validate_process(result)
            extractVariables = False if validProcess==False else self.extract_variables(result)
            if (validProcess == True and extractVariables == True):
                log.debug(f"NetConfStep process_step FETCH validProcess = {validProcess}")
                log.debug(f"NetConfStep process_step FETCH extractVariables = {extractVariables}")
                return 0
            else:
                log.debug(f"NetConfStep process_step FETCH validProcess = {validProcess}")
                log.debug(f"NetConfStep process_step FETCH extractVariables = {extractVariables}")
                raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.PROCESS_STEP_FETCH_ERROR, args={'validProcess': validProcess, 'extractVariables': extractVariables}).toJSON())
        elif self.type == 'EDIT':
            result = client.edit_config(self.payload)
            
            validProcess = self.validate_process(result)
            if validProcess == True:
                log.debug(f"NetConfStep process_step EDIT validProcess = {validProcess}")
                return 0
            else:
                log.debug(f"NetConfStep process_step EDIT validProcess = {validProcess}")
                raise ValueError(CustomNetconfError(payload=NETCONF_ERRORS.PROCESS_STEP_EDIT_ERROR, args={'validProcess': validProcess}).toJSON())