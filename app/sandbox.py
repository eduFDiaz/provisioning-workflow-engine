import asyncio, os

import logging
from Models.CliStep import CliStep
from Models.GrpcStep import GrpcStep
from Models.NetConfStep import NetConfStep
from Models.RestStep import RestStep
from Models.RestStep import exec_rest_step
from Models.CliStep import exec_cli_step
from Models.NetConfStep import exec_netconf_step
from Models.GrpcStep import exec_grpc_step

from Utils.Utils import read_yaml

from config import api_credentials

import xmltodict, json

from jsonpath_ng.ext import parser

FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='WORKFLOW_MS.log', filemode='a')

log = logging.getLogger()

from temporal_worker import start_temporal_worker

import config

from Services.Workflows.WorkflowService import invoke_steps
from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask

async def startup():
    log.info("Waiting for Temporal Worker to start up...")
    await asyncio.sleep(5)
    await start_temporal_worker(config.temporal_url,
                                config.temporal_namespace,
                                config.temporal_queue_name, 
                                [ExecuteRestTask,
                                 ExecuteCliTask,
                                 ExecuteNetConfTask,
                                 ExecuteGrpcTask], 
                                [exec_rest_step,
                                 exec_cli_step,
                                 exec_netconf_step,
                                 exec_grpc_step])

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

response_expected = """
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
exp_response_dict = xmltodict.parse(response_expected)
exp_response_json = json.dumps(exp_response_dict)

empty_fetch_response = """
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <data/>
</rpc-reply>
"""
empty_fetch_response_dict = xmltodict.parse(empty_fetch_response)
empty_fetch_response_json = json.dumps(empty_fetch_response)

edit_expected_response = """
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>
"""
edit_exp_response_dict = xmltodict.parse(edit_expected_response)
edit_exp_response_json = json.dumps(edit_expected_response)

edit_error_response = """
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
    <rpc-error xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <error-type>application</error-type>
        <error-tag>operation-failed</error-tag>
        <error-severity>error</error-severity>
        <error-path xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces">/rpc/edit-config/config/if:interfaces/if:interface[if:name='GigabitEthernet1/0/16']/if:type</error-path>
        <error-message lang="en"
            xmlns="https://www.w3.org/XML/1998/namespace">/interfaces/interface[name='GigabitEthernet1/0/16']/type: "Unsupported - value must be ethernetCsmacd or softwareLoopback"</error-message>
        <error-info>
            <bad-element>type</bad-element>
        </error-info>
    </rpc-error>
</rpc-reply>
"""
edit_error_response_dict = xmltodict.parse(edit_error_response)
edit_error_response_json = json.dumps(edit_error_response_dict)

def test_expected_response():
    #test jsonpath response for data not empty
    print(exp_response_dict)
    assert exp_response_dict.get('rpc-reply') != None
    assert exp_response_dict.get('rpc-reply').get('data') != None, "Data is not empty"

def test_empty_fetch_response():
    #test jsonpath response for data not empty
    print(exp_response_dict)
    assert edit_exp_response_dict.get('rpc-reply') != None
    assert edit_exp_response_dict.get('rpc-reply').get('data') == None, "Data is empty"

def test_exp_response_jsonpath_loopback():
    #json path expression to get the interface name
    value = '$..interface[?(@.description =~ ".*RESTCONF.*")].name'
    expected = ['Loopback109']

    path = value
    expression = parser.parse(path)
    
    data = json.loads(exp_response_json)

    print(json.dumps(data, indent=4, sort_keys=True))
    print(expression)
    result = [match.value for match in expression.find(data)]
    print(f"Result: {result} - Expected: {expected}")
    assert result == expected, "Expected result not found"

def test_exp_response_jsonpath_management():
    #json path expression to get the interface name
    value = '$..interface[?(@.description =~ ".*MANAGEMENT.*")]'
    expected = [{'name': 'GigabitEthernet1', 'description': "MANAGEMENT INTERFACE - DON'T TOUCH ME", 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'enabled': 'true', 'ipv4': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-ip', 'address': {'ip': '10.10.20.148', 'netmask': '255.255.255.0'}}, 'ipv6': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-ip'}}]

    path = value
    expression = parser.parse(path)
    
    data = json.loads(exp_response_json)

    print(json.dumps(data, indent=4, sort_keys=True))
    print(expression)
    result = [match.value for match in expression.find(data)]
    print(f"Result: {result} - Expected: {expected}")
    assert result == expected, "Expected result not found"

def test_ok_edit_response():
    #test jsonpath response for data not empty
    print(edit_exp_response_dict)
    assert edit_exp_response_dict.get('rpc-reply') != None
    assert edit_exp_response_dict.get('rpc-reply').get('ok') == None, "result is ok"

def test_error_edit_response():
    #test jsonpath response for data not empty
    print(edit_error_response_dict)
    assert edit_error_response_dict.get('rpc-error') != None, "result contains error"

if __name__ == "__main__":
    print("Running sandbox.py")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    loop.run_until_complete(invoke_steps())