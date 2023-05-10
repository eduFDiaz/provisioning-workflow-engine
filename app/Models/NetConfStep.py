from typing import Dict
from Clients.NetConfClient import NetConfClient
from Models.Base import Process
from Models.GlobalParams import Global_params
from config import logger as log
from config import api_credentials

import json
from jsonpath_ng.ext import parser
import xmltodict
import xml.etree.ElementTree as ET

global_params = Global_params()

from temporalio import activity

from typing import Optional, Union, Dict

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
    def validate_fetch_response(self, output_json) -> bool:
        """This method will validate attributes of the FETCH response against global_params"""
        log.debug(f"NetConfStep validate_fetch_response output_json\n{output_json}")
        
        if self.request is not None and self.request.get('validate') is not None:
            for key, value in self.request['validate'].items():
                log.debug(f"NetConfStep validate_fetch_response key: {key} value: {value}")
                
                try:
                    param = global_params.getitem(value)
                    log.debug(f"NetConfStep validate_fetch_response param: {param}")
                    
                    if param is None:
                        log.error(f"NetConfStep validate_fetch_response error: param {value} not found in global_params")
                        return False
                    
                    path = key
                    expression = parser.parse(path)
                    data = json.loads(output_json)
                    log.debug(f"NetConfStep validate_fetch_response data: {json.dumps(data, indent=4, sort_keys=True)}")  
                    log.debug(f"expression: {expression}")
                    result = [match.value for match in expression.find(data)]
                    
                    if result is None or len(result) == 0:
                        log.error(f"NetConfStep validate_fetch_response error: {path} not found in response")
                        return False
                    if (param != result):
                        log.error(f"NetConfStep validate_fetch_response error: {param} != {result}") 
                        return False
                except Exception as e:
                        log.error(f"NetConfStep validate_fetch_response error: {e}")
                        return False
        
        log.info("Code reached end of validate_fetch_response, no params to validate")
        return True
    def validate_edit_response(self, output_dic: Dict) -> bool:
        """This method will validate the netconf edit response"""
        log.debug(f"NetConfStep validate_edit_response output_dic\n{output_dic}")
        try:
            if output_dic['rpc-reply']['ok'] == None:
                log.info("NetConfStep response is </ok>")
                return True
        except KeyError as e:
            log.error(f"NetConfStep validate_process error: response was not </ok>: KeyError {e}")
            return False
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
                return False
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

        # client = NetConfClient(config)

        if self.type == 'FETCH':
            # result = client.get_filter(self.payload)
            result = """
            <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
            <data>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>GigabitEthernet1</name>
                    <description>MANAGEMENT INTERFACE - DON'T TOUCH ME</description>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.10.20.148</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                    </ipv4>
                    <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                </interface>
                <interface>
                    <name>Loopback0</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.0.0.1</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                    </ipv4>
                    <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                </interface>
                <interface>
                    <name>Loopback10</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                    <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                </interface>
                <interface>
                    <name>Loopback109</name>
                    <description>Configured by RESTCONF ga jadi</description>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.255.255.9</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                    </ipv4>
                    <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                </interface>
                <interface>
                    <name>VirtualPortGroup0</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:propVirtual</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>192.168.1.1</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                    </ipv4>
                    <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                </interface>
                </interfaces>
            </data>
            </rpc-reply>"""

            # result = """
            # <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
            #     <data/>
            # </rpc-reply>
            # """
            
            validProcess = self.validate_process(result)
            extractVariables = False if validProcess==False else self.extract_variables(result)
            if (validProcess == True and extractVariables == True):
                log.debug(f"NetConfStep process_step FETCH validProcess = {validProcess}")
                log.debug(f"NetConfStep process_step FETCH extractVariables = {extractVariables}")
                return 0
            else:
                log.debug(f"NetConfStep process_step FETCH validProcess = {validProcess}")
                log.debug(f"NetConfStep process_step FETCH extractVariables = {extractVariables}")
                return 1
        elif self.type == 'EDIT':
            # result = client.edit_config(self.payload)
            result = """
            <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                <ok/>
            </rpc-reply>
            """
            # result = """
            # <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
            #     <rpc-error xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
            #         <error-type>application</error-type>
            #         <error-tag>operation-failed</error-tag>
            #         <error-severity>error</error-severity>
            #         <error-path xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces">/rpc/edit-config/config/if:interfaces/if:interface[if:name='GigabitEthernet1/0/16']/if:type</error-path>
            #         <error-message lang="en"
            #             xmlns="https://www.w3.org/XML/1998/namespace">/interfaces/interface[name='GigabitEthernet1/0/16']/type: "Unsupported - value must be ethernetCsmacd or softwareLoopback"</error-message>
            #         <error-info>
            #             <bad-element>type</bad-element>
            #         </error-info>
            #     </rpc-error>
            # </rpc-reply>
            # """
            validProcess = self.validate_process(result)
            if validProcess == True:
                log.debug(f"NetConfStep process_step EDIT validProcess = {validProcess}")
                return 0
            else:
                log.debug(f"NetConfStep process_step EDIT validProcess = {validProcess}")
                return 1

@activity.defn
async def exec_netconf_step(conf: Dict) -> int:
    log.debug(f"NetConfStep exec_rest_step {conf}")
    step = NetConfStep(conf)
    result = step.process_step()
    log.debug(f"NetConfStep process_step {step} - {result}")
    return result