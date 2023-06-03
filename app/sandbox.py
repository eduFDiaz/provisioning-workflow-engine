import asyncio, os

import logging

from Models.GlobalParams import Global_params

global_params = Global_params()

from config import api_credentials

import xmltodict, json

from jsonpath_ng.ext import parser

from jinja2 import Environment, Template, FileSystemLoader

FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='WORKFLOW_MS.log', filemode='a')

log = logging.getLogger()

from temporal_worker import start_temporal_worker

import config

from Services.Workflows.WorkflowService import invoke_steps, get_steps_configs
from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from workflows.activities.activities import exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step

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

add_vrf_definition_exp_rendered_template = """
    <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <vrf operation="merge">
              <definition>
                <name>VRF_Capgemini</name>
                <rd>100:110</rd>
                <address-family>
                  <ipv4>
                    <export>
                      <map>Capgemini-VRF-EXPORT</map>
                    </export>
                    <import>
                      <map>Capgemini-VRF-IMPORT</map>
                    </import>
                  </ipv4>
                </address-family>
                <route-target>
                  <export>
                    <asn-ip>100:1000</asn-ip>
                  </export>
                  <import>
                    <asn-ip>100:1000</asn-ip>
                  </import>
                </route-target>
              </definition>
            </vrf>
          </native>
        </config>"""

add_vrf_definition_template = """
    <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <vrf operation="merge">
              <definition>
                <name>{{vrf[0][0].name}}</name>
                <rd>{{vrf[0][0].rd}}</rd>
                <address-family>
                  <ipv4>
                    <export>
                      <map>{{vrf[0][0]['ipv4-export'][0]}}</map>
                    </export>
                    <import>
                      <map>{{vrf[0][0]['ipv4-import'][0]}}</map>
                    </import>
                  </ipv4>
                </address-family>
                <route-target>
                {% for rt in vrf[0][0]['rt-export'] %}
                  <export>
                    <asn-ip>{{rt}}</asn-ip>
                  </export>
                {% endfor %}
                {% for rt in vrf[0][0]['rt-import'] %}
                  <import>
                    <asn-ip>{{rt}}</asn-ip>
                  </import>
                {% endfor %}
                </route-target>
              </definition>
            </vrf>
          </native>
        </config>"""

add_prefix_lists_exp_rendered_template = """
        <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <ip>
              <prefix-lists operation="merge">
                <prefixes>
                  <name>Capgemini-DC1-Management</name>
                  <no>10</no>
                  <action>permit</action>
                  <ip>192.168.187.0/28</ip>
                </prefixes>
              </prefix-lists>
              <prefix-list operation="merge">
                <prefixes>
                  <name>Capgemini-DC1-Management</name>
                  <seq>
                    <no>10</no>
                    <action>permit</action>
                    <ip>192.168.187.0/28</ip>
                  </seq>
                </prefixes>
              </prefix-list>
            </ip>
          </native>
        </config>
        """

add_prefix_lists_template = """
        <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <ip>
              <prefix-lists operation="merge">
              {% for pl in ip_prefix_list[0] %}
                <prefixes>
                  <name>{{pl['name']}}</name>
                  <no>{{pl['index']}}</no>
                  <action>{{pl['action']}}</action>
                  <ip>{{pl['prefix']}}</ip>
                </prefixes>
              {% endfor %}
              </prefix-lists>
              <prefix-list operation="merge">
              {% for pl in ip_prefix_list[0] %}
                <prefixes>
                  <name>{{pl['name']}}</name>
                  <seq>
                    <no>{{pl['index']}}</no>
                    <action>{{pl['action']}}</action>
                    <ip>{{pl['prefix']}}</ip>
                  </seq>
                </prefixes>
              {% endfor %}
              </prefix-list>
            </ip>
          </native>
        </config>
        """

add_route_map_exp_rendered_template = """
        <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <route-map operation="merge">
              <name>Capgemini-VRF-IMPORT</name>
              <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
                <seq_no>10</seq_no>
                <operation>permit</operation>
                <match>
                  <ip>
                    <address>
                      <prefix-list>Capgemini-DC1-Management</prefix-list>
                    </address>
                  </ip>
                </match>
              </route-map-without-order-seq>
              <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
                <seq_no>20</seq_no>
                <operation>permit</operation>
                <match>
                  <ip>
                    <address>
                      <prefix-list>Capgemini-DC2-Management</prefix-list>
                    </address>
                  </ip>
                </match>
              </route-map-without-order-seq>
            </route-map>
          </native>
        </config>
        """

add_route_maps_template = """
        <config>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          {% for rm in route_map[0] %}
            <route-map operation="merge">
              <name>{{rm['name']}}</name>
              {% for route in rm['match-list'] %}
              <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
                <seq_no>{{route['index']}}</seq_no>
                <operation>{{route['operation']}}</operation>
                <match>
                  <ip>
                    <address>
                      <prefix-list>{{route['prefix']}}</prefix-list>
                    </address>
                  </ip>
                </match>
              </route-map-without-order-seq>
              {% endfor %}
            </route-map>
          {% endfor %}
          </native>
        </config>
        """
params_init = {'interfaceName': ['GigabitEthernet1'], 'loopbackInterface': ['Loopback109'], 'name': 'phy_interface_vrf', 'log_forwarder_present': False, 'interfaces': ['GigabitEthernet1', 'GigabitEthernet2', 'GigabitEthernet3'], 'api_key': 'api_key_value', 'uuid': '7c277d3a-a11c-433a-a4a8-c9e6bc39a7a6', 'userId': 'palsa', 'interface_name': 'GigabitEthernet1', 'dns_name': '8.8.8.8', 'PL_AS_65003_IN': ['ip address 10.0.1.19', 'ip address 10.0.1.20', 'ip address 10.0.1.21'], 'ip_prefix_list': [[{'name': 'Capgemini-DC1-Management', 'index': 10, 'action': 'permit', 'prefix': '192.168.187.0/28'}]], 'route_map': [[{'name': 'Capgemini-VRF-IMPORT', 'match-list': [{'index': 10, 'operation': 'permit', 'prefix': 'Capgemini-DC1-Management'}, {'index': 20, 'operation': 'permit', 'prefix': 'Capgemini-DC2-Management'}]}]], 'vrf': [[{'name': 'VRF_Capgemini', 'rd': '100:110', 'rt-import': ['100:1000'], 'rt-export': ['100:1000'], 'ipv4-import': ['Capgemini-VRF-IMPORT'], 'ipv4-export': ['Capgemini-VRF-EXPORT']}]]}
for key, value in params_init.items():
  global_params.setitem(key, value)

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
    assert edit_error_response_dict.get('rpc-error') == None, "result contains error"

def test_add_vrf_definition_rendered_template():
    print(f"params - {global_params.getMap()}")
    print(f"vrf name - {global_params.getMap().get('vrf')[0][0]['name']}")
    template = Template(add_vrf_definition_template, trim_blocks=True, lstrip_blocks=True)
    renderedTemplate = template.render(**global_params.getMap())
    assert renderedTemplate == add_vrf_definition_exp_rendered_template, "rendered template is not as expected" 

def test_add_prefix_lists_rendered_template():
    print(f"params - {global_params.getMap()}")
    print(f"vrf name - {global_params.getMap().get('ip_prefix_list')[0][0]['name']}")
    template = Template(add_prefix_lists_template, trim_blocks=True, lstrip_blocks=True)
    renderedTemplate = template.render(**global_params.getMap())
    print(renderedTemplate)
    assert renderedTemplate == add_prefix_lists_exp_rendered_template, "rendered template is not as expected"

def test_add_route_maps_rendered_template():
    print(f"params - {global_params.getMap()}")
    print(f"vrf name - {global_params.getMap().get('route_map')[0][0]['name']}")
    template = Template(add_route_maps_template, trim_blocks=True, lstrip_blocks=True)
    renderedTemplate = template.render(**global_params.getMap())
    print(renderedTemplate)
    assert renderedTemplate == add_route_map_exp_rendered_template, "rendered template is not as expected"

if __name__ == "__main__":
    print("Running sandbox.py")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    # loop.run_until_complete(invoke_steps("phy_interface_vrf.yml"))
    # loop.run_until_complete(invoke_steps("master_flow.yml"))
    loop.run_until_complete(get_steps_configs("master_flow.yml","0c32b683-683a-4de4-a7f3-44318a14acbc"))
