import asyncio, os
from datetime import timedelta

import argparse
from dotenv import load_dotenv

parser = argparse.ArgumentParser(description="Load a .env file and print variables.")
parser.add_argument('--env-file', type=str, help='Path to the .env file')

# Parse arguments
args = parser.parse_args()

# Load .env file
load_dotenv(dotenv_path=args.env_file)

from Clients.CassandraConnection import CassandraConnection
from Models.Errors.ErrorMetadata import ErrorModel
from dao.ErrorDao import ErrorDao

from temporalClient import TemporalClient

from config import settings
from config import logger as log

from temporalio.exceptions import ApplicationError, ActivityError
from temporalio.client import WorkflowFailureError

# import logging

# import yaml

# from Models.GlobalParams import Global_params

# from config import api_credentials

# import xmltodict, json

# from jsonpath_ng.ext import parser

# from jinja2 import Environment, Template, FileSystemLoader

# FORMAT = "[%(asctime)s - %(levelname)s - %(filename)s:%(funcName)21s:%(lineno)s] %(message)s"
# logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%H:%M:%S', filename='WORKFLOW_MS.log', filemode='a')

# log = logging.getLogger()

from temporal_worker import start_temporal_worker

# import config

from Services.Workflows.WorkflowService import get_steps_configs, TemplateWorkflowArgs, TemplateWorkflow, TemplateChildWorkflow, workflowStatus
from Utils.Utils import fetch_template_files
from Services.Workflows.WorkflowService import get_steps_configs, RunTasks, run_TemplateWorkFlow
from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from workflows.activities.activities import read_template, clone_template, exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step

async def startup():
    log.info("Waiting for Temporal Worker to start up...")
    await asyncio.sleep(5)
    await start_temporal_worker(settings.temporal_server,
                                settings.temporal_namespace,
                                settings.temporal_queuename,
                                [TemplateWorkflow,
                                TemplateChildWorkflow,
                                ExecuteRestTask,
                                ExecuteCliTask,
                                ExecuteNetConfTask,
                                ExecuteGrpcTask], 
                                [read_template,
                                clone_template,
                                exec_rest_step,
                                exec_cli_step,
                                exec_netconf_step,
                                exec_grpc_step])

# response_expected = """
# <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
#   <data>
#     <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
#       <interface>
#         <name>GigabitEthernet1</name>
#         <description>MANAGEMENT INTERFACE - DON'T TOUCH ME</description>
#         <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
#         <enabled>true</enabled>
#         <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
#           <address>
#             <ip>10.10.20.148</ip>
#             <netmask>255.255.255.0</netmask>
#           </address>
#         </ipv4>
#         <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#       </interface>
#       <interface>
#         <name>Loopback0</name>
#         <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
#         <enabled>true</enabled>
#         <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
#           <address>
#             <ip>10.0.0.1</ip>
#             <netmask>255.255.255.0</netmask>
#           </address>
#         </ipv4>
#         <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#       </interface>
#       <interface>
#         <name>Loopback10</name>
#         <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
#         <enabled>true</enabled>
#         <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#         <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#       </interface>
#       <interface>
#         <name>Loopback109</name>
#         <description>Configured by RESTCONF ga jadi</description>
#         <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
#         <enabled>true</enabled>
#         <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
#           <address>
#             <ip>10.255.255.9</ip>
#             <netmask>255.255.255.0</netmask>
#           </address>
#         </ipv4>
#         <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#       </interface>
#       <interface>
#         <name>VirtualPortGroup0</name>
#         <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:propVirtual</type>
#         <enabled>true</enabled>
#         <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
#           <address>
#             <ip>192.168.1.1</ip>
#             <netmask>255.255.255.0</netmask>
#           </address>
#         </ipv4>
#         <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
#       </interface>
#     </interfaces>
#   </data>
# </rpc-reply>"""
# exp_response_dict = xmltodict.parse(response_expected)
# exp_response_json = json.dumps(exp_response_dict)

# response_after_netconf_vrf_steps = """
# <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
#   <data>
#     <app-hosting-cfg-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-app-hosting-cfg">
#       <apps>
#         <app>
#           <application-name>guestshell</application-name>
#           <application-network-resource>
#             <vnic-gateway-0>0</vnic-gateway-0>
#             <virtualportgroup-guest-interface-name-1>0</virtualportgroup-guest-interface-name-1>
#             <virtualportgroup-guest-ip-address-1>192.168.1.2</virtualportgroup-guest-ip-address-1>
#             <virtualportgroup-guest-ip-netmask-1>255.255.255.0</virtualportgroup-guest-ip-netmask-1>
#             <nameserver-0>8.8.8.8</nameserver-0>
#           </application-network-resource>
#         </app>
#       </apps>
#     </app-hosting-cfg-data>
#     <mdt-config-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg">
#       <mdt-subscription>
#         <subscription-id>101</subscription-id>
#         <base>
#           <stream>yang-push</stream>
#           <encoding>encode-kvgpb</encoding>
#           <period>100</period>
#           <xpath>/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-seconds</xpath>
#         </base>
#         <mdt-receivers>
#           <address>10.10.20.50</address>
#           <port>57500</port>
#           <protocol>grpc-tcp</protocol>
#         </mdt-receivers>
#       </mdt-subscription>
#     </mdt-config-data>
#     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#       <version>17.9</version>
#       <boot-start-marker/>
#       <boot-end-marker/>
#       <banner>
#         <login>
#           <banner>
# Welcome !!!!
# </banner>
#         </login>
#         <motd>
#           <banner>
# Welcome to the DevNet Sandbox for Cat8000V and IOS XE

# The following programmability features are already enabled:

# -NETCONF
# -RESTCONF

# Thanks for stopping by.
# </banner>
#         </motd>
#       </banner>
#       <memory>
#         <free>
#           <low-watermark>
#             <processor>63709</processor>
#           </low-watermark>
#         </free>
#       </memory>
#       <call-home>
#         <contact-email-addr xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-call-home">sch-smart-licensing@cisco.com</contact-email-addr>
#         <tac-profile xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-call-home">
#           <profile>
#             <CiscoTAC-1>
#               <active>true</active>
#               <destination>
#                 <transport-method>http</transport-method>
#               </destination>
#             </CiscoTAC-1>
#           </profile>
#         </tac-profile>
#       </call-home>
#       <service>
#         <timestamps>
#           <debug-config>
#             <datetime>
#               <msec/>
#             </datetime>
#           </debug-config>
#           <log-config>
#             <datetime>
#               <msec/>
#             </datetime>
#           </log-config>
#         </timestamps>
#         <call-home/>
#         <dhcp/>
#       </service>
#       <platform>
#         <console xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform">
#           <output>virtual</output>
#         </console>
#         <qfp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform">
#           <utilization>
#             <monitor>
#               <load>80</load>
#             </monitor>
#           </utilization>
#         </qfp>
#         <punt-keepalive xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform">
#           <disable-kernel-core>true</disable-kernel-core>
#         </punt-keepalive>
#       </platform>
#       <hostname>Cat8000V</hostname>
#       <username>
#         <name>admin</name>
#         <privilege>15</privilege>
#         <secret>
#           <encryption>9</encryption>
#           <secret>$9$lgJxy7Ga.Th5FU$gocFhcHC/8pvixGr.s2wB7X59FiGVvwYawfCPrmaJuY</secret>
#         </secret>
#       </username>
#       <username>
#         <name>tester</name>
#         <password>
#           <encryption>0</encryption>
#           <password>@@Today@@</password>
#         </password>
#       </username>
#       <vrf>
#         <definition>
#           <name>VRF_Capgemini</name>
#           <rd>100:110</rd>
#           <address-family>
#             <ipv4>
#               <export>
#                 <map>Capgemini-VRF-EXPORT</map>
#               </export>
#               <import>
#                 <map>Capgemini-VRF-IMPORT</map>
#               </import>
#             </ipv4>
#           </address-family>
#           <route-target>
#             <export>
#               <asn-ip>100:1000</asn-ip>
#             </export>
#             <import>
#               <asn-ip>100:1000</asn-ip>
#             </import>
#           </route-target>
#         </definition>
#       </vrf>
#       <ip>
#         <domain>
#           <name>cisco.com</name>
#         </domain>
#         <forward-protocol>
#           <protocol>nd</protocol>
#         </forward-protocol>
#         <ftp>
#           <passive/>
#         </ftp>
#         <multicast>
#           <route-limit xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">2147483647</route-limit>
#         </multicast>
#         <prefix-lists>
#           <prefixes>
#             <name>Capgemini-DC1-Management</name>
#             <no>10</no>
#             <action>permit</action>
#             <ip>192.168.187.0/28</ip>
#           </prefixes>
#           <prefixes>
#             <name>Capgemini-DC2-Management</name>
#             <no>20</no>
#             <action>permit</action>
#             <ip>192.168.187.0/28</ip>
#           </prefixes>
#         </prefix-lists>
#         <prefix-list>
#           <prefixes>
#             <name>Capgemini-DC1-Management</name>
#             <seq>
#               <no>10</no>
#               <action>permit</action>
#               <ip>192.168.187.0/28</ip>
#             </seq>
#           </prefixes>
#           <prefixes>
#             <name>Capgemini-DC2-Management</name>
#             <seq>
#               <no>20</no>
#               <action>permit</action>
#               <ip>192.168.187.0/28</ip>
#             </seq>
#           </prefixes>
#         </prefix-list>
#         <route>
#           <ip-route-interface-forwarding-list>
#             <prefix>0.0.0.0</prefix>
#             <mask>0.0.0.0</mask>
#             <fwd-list>
#               <fwd>GigabitEthernet1</fwd>
#               <interface-next-hop/>
#               <ip-address>10.10.20.254</ip-address>
#             </fwd-list>
#           </ip-route-interface-forwarding-list>
#         </route>
#       </ip>
#       <scp>
#         <server>
#           <enable/>
#         </server>
#       </scp>
#       <ssh>
#         <rsa>
#           <keypair-name>ssh-key</keypair-name>
#         </rsa>
#         <ssh-version>2</ssh-version>
#         <version>2</version>
#       </ssh>
#       <access-list>
#         <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
#           <name>IPv4-ACL</name>
#           <access-list-seq-rule>
#             <sequence>10</sequence>
#             <ace-rule>
#               <action>deny</action>
#               <protocol>tcp</protocol>
#               <any/>
#               <dest-ipv4-address>198.51.100.0</dest-ipv4-address>
#               <dest-mask>0.0.0.255</dest-mask>
#             </ace-rule>
#           </access-list-seq-rule>
#           <access-list-seq-rule>
#             <sequence>20</sequence>
#             <ace-rule>
#               <action>permit</action>
#               <protocol>tcp</protocol>
#               <any/>
#               <dst-any/>
#             </ace-rule>
#           </access-list-seq-rule>
#         </extended>
#         <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
#           <name>NAT-ACL</name>
#           <access-list-seq-rule>
#             <sequence>10</sequence>
#             <ace-rule>
#               <action>permit</action>
#               <protocol>ip</protocol>
#               <ipv4-address>192.168.1.0</ipv4-address>
#               <mask>0.0.0.255</mask>
#               <dst-any/>
#             </ace-rule>
#           </access-list-seq-rule>
#         </extended>
#         <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
#           <name>Test</name>
#           <access-list-seq-rule>
#             <sequence>10</sequence>
#             <ace-rule>
#               <action>permit</action>
#               <protocol>ip</protocol>
#               <any/>
#               <dst-host-address>1.1.1.1</dst-host-address>
#               <dst-host>1.1.1.1</dst-host>
#             </ace-rule>
#           </access-list-seq-rule>
#         </extended>
#       </access-list>
#       <http xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-http">
#         <authentication>
#           <local/>
#         </authentication>
#         <server>true</server>
#         <secure-server>true</secure-server>
#       </http>
#       <igmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-igmp">
#         <snooping>
#           <querier/>
#         </snooping>
#       </igmp>
#       <nat xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
#         <inside>
#           <source>
#             <list-interface>
#               <list>
#                 <id>NAT-ACL</id>
#                 <interface>
#                   <name>GigabitEthernet1</name>
#                   <overload-new/>
#                 </interface>
#               </list>
#             </list-interface>
#             <list>
#               <id>NAT-ACL</id>
#               <interface>
#                 <name>GigabitEthernet1</name>
#                 <overload/>
#               </interface>
#             </list>
#           </source>
#         </inside>
#       </nat>
#       <nbar xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-nbar">
#         <classification>
#           <dns>
#             <classify-by-domain/>
#           </dns>
#         </classification>
#       </nbar>
#     </native>
#     <interface>
#       <GigabitEthernet>
#         <name>1</name>
#         <description>MANAGEMENT INTERFACE - DON'T TOUCH ME</description>
#         <switchport>
#           <trunk xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
#             <native>
#               <vlan-config>
#                 <tag>true</tag>
#               </vlan-config>
#             </native>
#           </trunk>
#         </switchport>
#         <ip>
#           <address>
#             <primary>
#               <address>10.10.20.48</address>
#               <mask>255.255.255.0</mask>
#             </primary>
#           </address>
#         </ip>
#         <logging>
#           <event>
#             <link-status/>
#           </event>
#         </logging>
#         <access-session>
#           <host-mode>multi-auth</host-mode>
#         </access-session>
#         <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
#           <auto>true</auto>
#         </negotiation>
#       </GigabitEthernet>
#       <GigabitEthernet>
#         <name>2</name>
#         <description>Network Interface</description>
#         <switchport>
#           <trunk xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
#             <native>
#               <vlan-config>
#                 <tag>true</tag>
#               </vlan-config>
#             </native>
#           </trunk>
#         </switchport>
#         <shutdown/>
#         <logging>
#           <event>
#             <link-status/>
#           </event>
#         </logging>
#         <access-session>
#           <host-mode>multi-auth</host-mode>
#         </access-session>
#         <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
#           <auto>true</auto>
#         </negotiation>
#       </GigabitEthernet>
#       <GigabitEthernet>
#         <name>3</name>
#         <description>Network Interface</description>
#         <switchport>
#           <trunk xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
#             <native>
#               <vlan-config>
#                 <tag>true</tag>
#               </vlan-config>
#             </native>
#           </trunk>
#         </switchport>
#         <shutdown/>
#         <logging>
#           <event>
#             <link-status/>
#           </event>
#         </logging>
#         <access-session>
#           <host-mode>multi-auth</host-mode>
#         </access-session>
#         <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
#           <auto>true</auto>
#         </negotiation>
#       </GigabitEthernet>
#       <Loopback>
#         <name>0</name>
#         <description>smruti</description>
#         <ip>
#           <address>
#             <primary>
#               <address>10.0.0.1</address>
#               <mask>255.255.255.0</mask>
#             </primary>
#           </address>
#         </ip>
#         <logging>
#           <event>
#             <link-status/>
#           </event>
#         </logging>
#       </Loopback>
#       <Loopback>
#         <name>10</name>
#         <logging>
#           <event>
#             <link-status/>
#           </event>
#         </logging>
#       </Loopback>
#       <Loopback>
#         <name>109</name>
#         <description>Configured by RESTCONF ga jadi</description>
#         <ip>
#           <address>
#             <primary>
#               <address>10.255.255.9</address>
#               <mask>255.255.255.0</mask>
#             </primary>
#           </address>
#         </ip>
#         <logging>
#           <event/>
#           <link-status/>
#         </logging>
#       </Loopback>
#     </interface>
#     <Loopback>
#       <name>5689</name>
#       <description>Configured_using_Python_netmiko_by_Munia</description>
#       <ip>
#         <address>
#           <primary>
#             <address>10.56.89.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>8585</name>
#       <description>This Is Dog</description>
#       <ip>
#         <address>
#           <primary>
#             <address>10.146.185.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>8686</name>
#       <description>Task7</description>
#       <shutdown/>
#       <ip>
#         <address>
#           <primary>
#             <address>10.146.186.2</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>14670</name>
#       <description>Task7-pod3</description>
#       <shutdown/>
#       <ip>
#         <address>
#           <secondary>
#             <address>10.146.1.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <secondary>
#             <address>10.146.4.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <secondary>
#             <address>10.146.9.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <secondary>
#             <address>10.146.10.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <secondary>
#             <address>14.146.12.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <primary>
#             <address>10.146.3.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>14671</name>
#       <description>This is a TEST2 Loopback</description>
#       <ip>
#         <address>
#           <secondary>
#             <address>10.147.9.1</address>
#             <mask>255.255.255.255</mask>
#             <secondary/>
#           </secondary>
#           <primary>
#             <address>10.147.4.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>146711</name>
#       <description>T11</description>
#       <ip>
#         <address>
#           <primary>
#             <address>10.146.11.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <Loopback>
#       <name>146799</name>
#       <description>This is kitty meow</description>
#       <ip>
#         <address>
#           <primary>
#             <address>10.146.99.1</address>
#             <mask>255.255.255.255</mask>
#           </primary>
#         </address>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </Loopback>
#     <VirtualPortGroup>
#       <name>0</name>
#       <ip>
#         <address>
#           <primary>
#             <address>192.168.1.1</address>
#             <mask>255.255.255.0</mask>
#           </primary>
#         </address>
#         <nat xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
#           <inside/>
#         </nat>
#       </ip>
#       <logging>
#         <event>
#           <link-status/>
#         </event>
#       </logging>
#     </VirtualPortGroup>
#   </data>
#   <route-map>
#     <name>Capgemini-VRF-IMPORT</name>
#     <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
#       <seq_no>10</seq_no>
#       <operation>permit</operation>
#       <match>
#         <ip>
#           <address>
#             <prefix-list>Capgemini-DC1-Management</prefix-list>
#           </address>
#         </ip>
#       </match>
#     </route-map-without-order-seq>
#     <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
#       <seq_no>20</seq_no>
#       <operation>permit</operation>
#       <match>
#         <ip>
#           <address>
#             <prefix-list>Capgemini-DC2-Management</prefix-list>
#           </address>
#         </ip>
#       </match>
#     </route-map-without-order-seq>
#   </route-map>
#   <control-plane/>
#   <logging>
#     <console-config>
#       <console>false</console>
#     </console-config>
#     <console-conf>
#       <console>false</console>
#     </console-conf>
#   </logging>
#   <login>
#     <on-success>
#       <log/>
#     </on-success>
#   </login>
#   <multilink>
#     <bundle-name xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ppp">authenticated</bundle-name>
#   </multilink>
#   <redundancy/>
#   <subscriber>
#     <templating/>
#   </subscriber>
#   <ethernet>
#     <cfm xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
#       <alarm>
#         <delay>2500</delay>
#         <reset>10000</reset>
#       </alarm>
#     </cfm>
#   </ethernet>
#   <crypto>
#     <ikev2 xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-crypto">
#       <http-url>
#         <cert/>
#       </http-url>
#     </ikev2>
#     <pki xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-crypto">
#       <certificate>
#         <chain>
#           <name>SLA-TrustPoint</name>
#           <certificate>
#             <serial>01</serial>
#             <certtype>ca</certtype>
#           </certificate>
#         </chain>
#         <chain>
#           <name>TP-self-signed-3209586145</name>
#           <certificate>
#             <serial>01</serial>
#             <certtype>self-signed</certtype>
#           </certificate>
#         </chain>
#       </certificate>
#       <trustpoint>
#         <id>SLA-TrustPoint</id>
#         <enrollment>
#           <enrollment-method>
#             <pkcs12/>
#           </enrollment-method>
#           <pkcs12/>
#         </enrollment>
#         <revocation-check>crl</revocation-check>
#       </trustpoint>
#       <trustpoint>
#         <id>TP-self-signed-3209586145</id>
#         <enrollment>
#           <enrollment-method>
#             <selfsigned/>
#           </enrollment-method>
#           <selfsigned/>
#         </enrollment>
#         <revocation-check>none</revocation-check>
#         <rsakeypair>
#           <key-label>TP-self-signed-3209586145</key-label>
#         </rsakeypair>
#         <subject-name>cn=IOS-Self-Signed-Certificate-3209586145</subject-name>
#       </trustpoint>
#     </pki>
#   </crypto>
#   <license>
#     <udi>
#       <pid>C8000V</pid>
#       <sn>9UWS2FADP45</sn>
#     </udi>
#   </license>
#   <standby>
#     <redirects>true</redirects>
#   </standby>
#   <line>
#     <aux>
#       <first>0</first>
#     </aux>
#     <console>
#       <first>0</first>
#       <exec-timeout>
#         <minutes>0</minutes>
#         <seconds>0</seconds>
#       </exec-timeout>
#       <stopbits>1</stopbits>
#     </console>
#     <vty>
#       <first>0</first>
#       <last>4</last>
#       <length>0</length>
#       <login>
#         <local/>
#       </login>
#       <transport>
#         <input>
#           <input>ssh</input>
#         </input>
#       </transport>
#     </vty>
#   </line>
#   <iox/>
#   <diagnostic xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-diagnostics">
#     <bootup>
#       <level>minimal</level>
#     </bootup>
#   </diagnostic>
# </rpc-reply>
# """
# response_after_netconf_vrf_steps_dict = xmltodict.parse(response_after_netconf_vrf_steps)
# response_after_netconf_vrf_steps_json = json.dumps(response_after_netconf_vrf_steps_dict)

# empty_fetch_response = """
# <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
#   <data/>
# </rpc-reply>
# """
# empty_fetch_response_dict = xmltodict.parse(empty_fetch_response)
# empty_fetch_response_json = json.dumps(empty_fetch_response)

# edit_expected_response = """
# <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
#   <ok/>
# </rpc-reply>
# """
# edit_exp_response_dict = xmltodict.parse(edit_expected_response)
# edit_exp_response_json = json.dumps(edit_expected_response)

# edit_error_response = """
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
# edit_error_response_dict = xmltodict.parse(edit_error_response)
# edit_error_response_json = json.dumps(edit_error_response_dict)

# add_vrf_definition_exp_rendered_template = """
#     <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#             <vrf operation="merge">
#               <definition>
#                 <name>VRF_Capgemini</name>
#                 <rd>100:110</rd>
#                 <address-family>
#                   <ipv4>
#                     <export>
#                       <map>Capgemini-VRF-EXPORT</map>
#                     </export>
#                     <import>
#                       <map>Capgemini-VRF-IMPORT</map>
#                     </import>
#                   </ipv4>
#                 </address-family>
#                 <route-target>
#                   <export>
#                     <asn-ip>100:1000</asn-ip>
#                   </export>
#                   <import>
#                     <asn-ip>100:1000</asn-ip>
#                   </import>
#                 </route-target>
#               </definition>
#             </vrf>
#           </native>
#         </config>"""

# add_vrf_definition_template = """
#     <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#             <vrf operation="merge">
#               <definition>
#                 <name>{{vrf[0][0].name}}</name>
#                 <rd>{{vrf[0][0].rd}}</rd>
#                 <address-family>
#                   <ipv4>
#                     <export>
#                       <map>{{vrf[0][0]['ipv4-export'][0]}}</map>
#                     </export>
#                     <import>
#                       <map>{{vrf[0][0]['ipv4-import'][0]}}</map>
#                     </import>
#                   </ipv4>
#                 </address-family>
#                 <route-target>
#                 {% for rt in vrf[0][0]['rt-export'] %}
#                   <export>
#                     <asn-ip>{{rt}}</asn-ip>
#                   </export>
#                 {% endfor %}
#                 {% for rt in vrf[0][0]['rt-import'] %}
#                   <import>
#                     <asn-ip>{{rt}}</asn-ip>
#                   </import>
#                 {% endfor %}
#                 </route-target>
#               </definition>
#             </vrf>
#           </native>
#         </config>"""

# add_prefix_lists_exp_rendered_template = """
#         <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#             <ip>
#               <prefix-lists operation="merge">
#                 <prefixes>
#                   <name>Capgemini-DC1-Management</name>
#                   <no>10</no>
#                   <action>permit</action>
#                   <ip>192.168.187.0/28</ip>
#                 </prefixes>
#               </prefix-lists>
#               <prefix-list operation="merge">
#                 <prefixes>
#                   <name>Capgemini-DC1-Management</name>
#                   <seq>
#                     <no>10</no>
#                     <action>permit</action>
#                     <ip>192.168.187.0/28</ip>
#                   </seq>
#                 </prefixes>
#               </prefix-list>
#             </ip>
#           </native>
#         </config>
#         """

# add_prefix_lists_template = """
#         <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#             <ip>
#               <prefix-lists operation="merge">
#               {% for pl in ip_prefix_list[0] %}
#                 <prefixes>
#                   <name>{{pl['name']}}</name>
#                   <no>{{pl['index']}}</no>
#                   <action>{{pl['action']}}</action>
#                   <ip>{{pl['prefix']}}</ip>
#                 </prefixes>
#               {% endfor %}
#               </prefix-lists>
#               <prefix-list operation="merge">
#               {% for pl in ip_prefix_list[0] %}
#                 <prefixes>
#                   <name>{{pl['name']}}</name>
#                   <seq>
#                     <no>{{pl['index']}}</no>
#                     <action>{{pl['action']}}</action>
#                     <ip>{{pl['prefix']}}</ip>
#                   </seq>
#                 </prefixes>
#               {% endfor %}
#               </prefix-list>
#             </ip>
#           </native>
#         </config>
#         """

# add_route_map_exp_rendered_template = """
#         <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#             <route-map operation="merge">
#               <name>Capgemini-VRF-IMPORT</name>
#               <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
#                 <seq_no>10</seq_no>
#                 <operation>permit</operation>
#                 <match>
#                   <ip>
#                     <address>
#                       <prefix-list>Capgemini-DC1-Management</prefix-list>
#                     </address>
#                   </ip>
#                 </match>
#               </route-map-without-order-seq>
#               <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
#                 <seq_no>20</seq_no>
#                 <operation>permit</operation>
#                 <match>
#                   <ip>
#                     <address>
#                       <prefix-list>Capgemini-DC2-Management</prefix-list>
#                     </address>
#                   </ip>
#                 </match>
#               </route-map-without-order-seq>
#             </route-map>
#           </native>
#         </config>
#         """

# add_route_maps_template = """
#         <config>
#           <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#           {% for rm in route_map[0] %}
#             <route-map operation="merge">
#               <name>{{rm['name']}}</name>
#               {% for route in rm['match-list'] %}
#               <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
#                 <seq_no>{{route['index']}}</seq_no>
#                 <operation>{{route['operation']}}</operation>
#                 <match>
#                   <ip>
#                     <address>
#                       <prefix-list>{{route['prefix']}}</prefix-list>
#                     </address>
#                   </ip>
#                 </match>
#               </route-map-without-order-seq>
#               {% endfor %}
#             </route-map>
#           {% endfor %}
#           </native>
#         </config>
#         """

# config_customer_vrf_template = """
#   terminal length 0
#   enable
#   config t
#   {% for rm in route_map[0] %}
#   {% for pl in ip_prefix_list[0] %}
#   ip prefix-list {{pl['name']}} seq {{pl['index']}} {{pl['action']}} {{pl['prefix']}}
#   {% endfor %}
#   {% for route in rm['match-list'] %}
#   route-map {{rm['name']}} {{route['operation']}} {{route['index']}}
#   match ip address prefix-list {{route['prefix']}}
#   exit
#   {% endfor %}
#   {% endfor %}
#   vrf definition {{vrf[0][0].name}}
#   rd {{vrf[0][0].rd}}
#   {% for rt in vrf[0][0]['rt-export'] %}
#   route-target export {{rt}}
#   {% endfor %}
#   {% for rt in vrf[0][0]['rt-export'] %}
#   route-target import {{rt}}
#   {% endfor %}
#   address-family ipv4
#   import map {{vrf[0][0]['ipv4-import'][0]}}
#   export map {{vrf[0][0]['ipv4-export'][0]}}
#   exit-address-family
#   end
#   """

# config_customer_vrf_rendered_template = """
#   terminal length 0
#   enable
#   config t
#   ip prefix-list Capgemini-DC1-Management seq 10 permit 192.168.187.0/28
#   route-map Capgemini-VRF-IMPORT permit 10
#   match ip address prefix-list Capgemini-DC1-Management
#   exit
#   route-map Capgemini-VRF-IMPORT permit 20
#   match ip address prefix-list Capgemini-DC2-Management
#   exit
#   vrf definition VRF_Capgemini
#   rd 100:110
#   route-target export 100:1000
#   route-target import 100:1000
#   address-family ipv4
#   import map Capgemini-VRF-IMPORT
#   export map Capgemini-VRF-EXPORT
#   exit-address-family
#   end
#   """

# # uncomment ONLY to run the jinja rendenring tests, when running workflows
# # the global params dict will be updated by the workflow activities
# correlationID = '0c32b683-683a-4de4-a7f3-44318a14acbc'
# params_init = {'interfaceName': ['GigabitEthernet1'], 'loopbackInterface': ['Loopback109'], 'name': 'phy_interface_vrf', 'log_forwarder_present': False, 'interfaces': ['GigabitEthernet1', 'GigabitEthernet2', 'GigabitEthernet3'], 'api_key': 'api_key_value', 'uuid': '0c32b683-683a-4de4-a7f3-44318a14acbc', 'userId': 'palsa', 'interface_name': 'GigabitEthernet1', 'dns_name': '8.8.8.8', 'PL_AS_65003_IN': ['ip address 10.0.1.19', 'ip address 10.0.1.20', 'ip address 10.0.1.21'], 'ip_prefix_list': [[{'name': 'Capgemini-DC1-Management', 'index': 10, 'action': 'permit', 'prefix': '192.168.187.0/28'}]], 'route_map': [[{'name': 'Capgemini-VRF-IMPORT', 'match-list': [{'index': 10, 'operation': 'permit', 'prefix': 'Capgemini-DC1-Management'}, {'index': 20, 'operation': 'permit', 'prefix': 'Capgemini-DC2-Management'}]}]], 'vrf': [[{'name': 'VRF_Capgemini', 'rd': '100:110', 'rt-import': ['100:1000'], 'rt-export': ['100:1000'], 'ipv4-import': ['Capgemini-VRF-IMPORT'], 'ipv4-export': ['Capgemini-VRF-EXPORT']}]]}
# # params_init = {}

# global_params = Global_params().getMap(correlationID)
# print(global_params)

# for key, value in params_init.items():
#   global_params[key] = value

# def test_expected_response():
#     #test jsonpath response for data not empty
#     print(exp_response_dict)
#     assert exp_response_dict.get('rpc-reply') != None
#     assert exp_response_dict.get('rpc-reply').get('data') != None, "Data is not empty"

# def test_empty_fetch_response():
#     #test jsonpath response for data not empty
#     print(exp_response_dict)
#     assert edit_exp_response_dict.get('rpc-reply') != None
#     assert edit_exp_response_dict.get('rpc-reply').get('data') == None, "Data is empty"

# def test_exp_response_jsonpath_loopback():
#     #json path expression to get the interface name
#     value = '$..interface[?(@.description =~ ".*RESTCONF.*")].name'
#     expected = ['Loopback109']

#     path = value
#     expression = parser.parse(path)
    
#     data = json.loads(exp_response_json)

#     print(json.dumps(data, indent=4, sort_keys=True))
#     print(expression)
#     result = [match.value for match in expression.find(data)]
#     print(f"Result: {result} - Expected: {expected}")
#     assert result == expected, "Expected result not found"

# def test_exp_response_jsonpath_management():
#     #json path expression to get the interface name
#     value = '$..interface[?(@.description =~ ".*MANAGEMENT.*")]'
#     expected = [{'name': 'GigabitEthernet1', 'description': "MANAGEMENT INTERFACE - DON'T TOUCH ME", 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'enabled': 'true', 'ipv4': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-ip', 'address': {'ip': '10.10.20.148', 'netmask': '255.255.255.0'}}, 'ipv6': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-ip'}}]

#     path = value
#     expression = parser.parse(path)
    
#     data = json.loads(exp_response_json)

#     print(json.dumps(data, indent=4, sort_keys=True))
#     print(expression)
#     result = [match.value for match in expression.find(data)]
#     print(f"Result: {result} - Expected: {expected}")
#     assert result == expected, "Expected result not found"

# def test_ok_edit_response():
#     #test jsonpath response for data not empty
#     print(edit_exp_response_dict)
#     assert edit_exp_response_dict.get('rpc-reply').get('rpc-error') == None

# def test_error_edit_response():
#     #test jsonpath response for data not empty
#     print(edit_error_response_dict)
#     assert edit_error_response_dict.get('rpc-reply').get('rpc-error') != None, "result contains error"

# def test_add_vrf_definition_rendered_template():
#     print(f"params - {global_params}")
#     print(f"vrf name - {global_params.get('vrf')[0][0]['name']}")
#     template = Template(add_vrf_definition_template, trim_blocks=True, lstrip_blocks=True)
#     renderedTemplate = template.render(**global_params)
#     assert renderedTemplate == add_vrf_definition_exp_rendered_template, "rendered template is not as expected" 

# def test_add_prefix_lists_rendered_template():
#     print(f"params - {global_params}")
#     print(f"vrf name - {global_params.get('ip_prefix_list')[0][0]['name']}")
#     template = Template(add_prefix_lists_template, trim_blocks=True, lstrip_blocks=True)
#     renderedTemplate = template.render(**global_params)
#     print(renderedTemplate)
#     assert renderedTemplate == add_prefix_lists_exp_rendered_template, "rendered template is not as expected"

# def test_add_route_maps_rendered_template():
#     print(f"params - {global_params}")
#     print(f"vrf name - {global_params.get('route_map')[0][0]['name']}")
#     template = Template(add_route_maps_template, trim_blocks=True, lstrip_blocks=True)
#     renderedTemplate = template.render(**global_params)
#     print(renderedTemplate)
#     assert renderedTemplate == add_route_map_exp_rendered_template, "rendered template is not as expected"

# def test_config_vrf_rendered_template():
#     print(f"params - {global_params}")
#     print(f"vrf name - {global_params.get('vrf')[0][0]['name']}")
#     template = Template(config_customer_vrf_template, trim_blocks=True, lstrip_blocks=True)
#     renderedTemplate = template.render(**global_params)
#     print(renderedTemplate)
#     assert renderedTemplate == config_customer_vrf_rendered_template, "rendered template is not as expected"

# def test_validate_netconf_vrf_steps():
#     print(f"response_after_netconf_vrf_steps_json - {response_after_netconf_vrf_steps_json}")

#     yaml_string = """
#     vrf_validate:
#       definition:
#         name: VRF_Capgemini
#         rd: 100:110
#         address-family:
#           ipv4:
#             export:
#               map: Capgemini-VRF-EXPORT
#             import:
#               map: Capgemini-VRF-IMPORT
#         route-target:
#           export:
#             asn-ip: 100:1000
#           import:
#             asn-ip: 100:1000
#     prefix-lists-validate:
#       prefixes:
#         - name: Capgemini-DC1-Management
#           "no": "10"
#           action: permit
#           ip: 192.168.187.0/28
#         - name: Capgemini-DC2-Management
#           "no": "20"
#           action: permit
#           ip: 192.168.187.0/28
#     route-map-validate:
#       name: Capgemini-VRF-IMPORT
#       route-map-without-order-seq:
#         - "@xmlns": http://cisco.com/ns/yang/Cisco-IOS-XE-route-map
#           seq_no: "10"
#           operation: permit
#           match:
#             ip:
#               address:
#                 prefix-list: Capgemini-DC1-Management
#         - "@xmlns": http://cisco.com/ns/yang/Cisco-IOS-XE-route-map
#           seq_no: "20"
#           operation: permit
#           match:
#             ip:
#               address:
#                 prefix-list: Capgemini-DC2-Management
#     validate:
#       $..data.native.vrf: vrf_validate
#       $..data.native.ip['prefix-lists']: prefix-lists-validate
#       $..['route-map']: route-map-validate
#     """

#     params_dict = yaml.load(yaml_string, Loader=yaml.FullLoader)
#     print(f"################## params_dict - {params_dict}")

#     for key, value in params_dict.get('validate').items():
#         print(f"########## key - {key}")
#         print(f"##########  value - {value}")
#         path = key

#         expression = parser.parse(path)
        
#         data = json.loads(response_after_netconf_vrf_steps_json)

#         print(f"############# expression - {expression}")

#         result = [match.value for match in expression.find(data)]
#         print(f"Result: {result[0]} - \nExpected: {params_dict.get(value)}")
#         assert result[0] == params_dict.get(value), "Expected param not found"   

if __name__ == "__main__":
    print("Running sandbox.py")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    
    # taskList = {}
    # # run_TemplateWorkFlow will run synchronously

    # try:
    #     taskList = loop.run_until_complete(run_TemplateWorkFlow(flowFileName="l3vpn-provisioning/vpn_provisioning.yml",request_id="0c32b683-683a-4de4-a7f3-44318a14acbc", repoName="network-workflows", branch="feature-issues-18"))
    # except Exception as error:
    #     log.error(error)
    #     exit(1)

    # if there are no errors will call RunTasks for the taskList result of cloning and reading the templates
    # log.debug(f"taskList len - {len(taskList)}")
    # runTasksResult = loop.run_until_complete(RunTasks(taskList))
    # log.debug(f"runTasksResult - {runTasksResult}")
    # try:
    #     fetch_template_files(wfFileName="l3vpn-provisioning/vpn_provisioning.yml", repoName="network-workflows", branch="feature-issues-18")
    # except Exception as error:
    #     log.error(error)
    #     exit(1)

    # taskList = loop.run_until_complete(read_template("l3vpn-provisioning/vpn_provisioning.yml", "d3926a0a-85b9-4758-98d8-42bfb3023904"))
    # log.debug(f"taskList len - {len(taskList)}")
    # log.debug(f"pe config {taskList}")
    # runTasksResult = loop.run_until_complete(RunTasks(taskList))
    # log.debug(f"runTasksResult - {runTasksResult}")

    response = loop.run_until_complete(workflowStatus(request_id="d3926a0a-85b9-4758-98d8-42bfb3023904", workflowFileName="l3vpn-provisioning/vpn_provisioning.yml"))
    #log response body and status
    log.debug(f"response - {response.body} , status - {response.status_code}")

    # connection = CassandraConnection()
    # session = connection.get_session()
    # error_dao = ErrorDao(session)
    # error = ErrorModel(correlationID="d3926a0a-85b9-4758-98d8-42bfb3023904", timeStamp="eeeee",error="test error")
    # error_dao.add_or_update_error(error)

