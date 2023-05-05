import logging
from scrapli_netconf.driver import NetconfDriver
# Suppress the client logs only to CRITICAL only as
# it was bloating the log file with too much info
log = logging.getLogger('scrapli')
log.setLevel(logging.CRITICAL)

class NetConfClient:
    """A class to represent a NetConf Client"""
    def __init__(self, config):
        self.device = config
        self.conn = NetconfDriver(**self.device)
        self.conn.open()
    
    def __del__(self):
        log.critical("Closing NetConf connection")
        self.conn.close()

    def get_filter(self, payload):
        result = self.conn.get_config(filter_ = payload, filter_type="subtree", source="running")
        return result.result

    def edit_config(self, config):
        result = self.conn.edit_config(config=config, target="candidate")
        return result.result
    
    def commit(self):
        result = self.conn.commit()
        return result.result

# INTERFACE_GB1_FILTER = """
# <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
#   <interface>
#     <name>GigabitEthernet1</name>
#   </interface>
# </interfaces>
# """

# BANNER_FILTER = """
#     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#         <banner>
#         </banner>
#     </native>
# """

# EDIT_BANNER = """
#     <config>
#         <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#           <banner operation="replace">
#             <motd>
#               <banner>Hello there CSR</banner>
#             </motd>
#           </banner>
#         </native>
#     </config>
# """
# # Usage
# my_device = {
#     "host": "sandbox-iosxe-latest-1.cisco.com",
#     "auth_username": "admin",
#     "auth_password": "C1sco12345",
#     "auth_strict_key": False,
#     "port": 830
# }

# client = NetConfClient(my_device)

# result = client.get_filter(INTERFACE_GB1_FILTER)
# print(result)

# result.result = """
# <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
#   <data>
#     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
#       <banner>
#         <motd>
#           <banner>Hello there CSR</banner>
#         </motd>
#       </banner>
#     </native>
#     <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
#       <interface>
#         <name>GigabitEthernet1</name>
#         <description>Added by Eduardo</description>
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
#     </interfaces>
#   </data>
# </rpc-reply>
# """
# resDictionary = xmltodict.parse(result.result)
# print(resDictionary)
# print("resDictionary {}", resDictionary['rpc-reply']['data']['interfaces']['interface']['name'])

# # Parse the XML response and create an ElementTree object
# root = ET.fromstring(result.result)

# # Use XPath to query the ElementTree object for the enabled interfaces
# print(root.find('.//{urn:ietf:params:xml:ns:yang:ietf-interfaces}name').text)

# #print banner motd
# print(root.find('.//{http://cisco.com/ns/yang/Cisco-IOS-XE-native}banner/{http://cisco.com/ns/yang/Cisco-IOS-XE-native}motd/{http://cisco.com/ns/yang/Cisco-IOS-XE-native}banner').text)

# # result = conn.edit_config(config=EDIT_BANNER, target="candidate")
# # print(result.result)

# # result = conn.commit()
# # print(result.result)