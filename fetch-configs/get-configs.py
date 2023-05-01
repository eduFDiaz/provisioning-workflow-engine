from ncclient import manager
import xml.etree.ElementTree as ET

# Constants
HOST = "sandbox-iosxe-latest-1.cisco.com"
PORT = 830
USERNAME = "admin"
PASSWORD = "C1sco12345"

# Connect to the NETCONF server
with manager.connect(host=HOST, port=PORT, username=USERNAME, password=PASSWORD, hostkey_verify=False) as m:

    # Get the current configuration
    config = m.get_config(source="running", filter=('subtree', "<interfaces/>")).data_xml
    config_tree = ET.fromstring(config)

    # Read interface names, descriptions and enabled status
    interfaces = config_tree.findall(".//{urn:ietf:params:xml:ns:yang:ietf-interfaces}interface/{urn:ietf:params:xml:ns:yang:ietf-interfaces}name")
    descriptions = config_tree.findall(".//{urn:ietf:params:xml:ns:yang:ietf-interfaces}interface/{urn:ietf:params:xml:ns:yang:ietf-interfaces}description")
    status = config_tree.findall(".//{urn:ietf:params:xml:ns:yang:ietf-interfaces}interface/{urn:ietf:params:xml:ns:yang:ietf-interfaces}enabled")    

    for (interface, description, enabled) in zip(interfaces, descriptions, status):
        print(f"Interface {interface.text} has description: {description.text} and is enabled: {enabled.text}")
    