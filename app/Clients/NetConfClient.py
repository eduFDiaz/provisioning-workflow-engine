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
        if payload == None or payload == "":
            # if no payload is provided, get the entire config
            result = self.conn.get_config(source="running")
        else:
            # if a payload is provided, get the config based on a subtree filter
            result = self.conn.get_config(filter_ = payload, filter_type="subtree", source="running")
        return result.result

    def edit_config(self, config):
        result = self.conn.edit_config(config=config, target="running")
        return result.result
    
    def commit(self):
        result = self.conn.commit()
        return result.result

# config = {
#     "host": "sandbox-iosxe-latest-1.cisco.com",
#     "auth_username": "admin",
#     "auth_password": "C1sco12345",
#     "auth_strict_key": False,
#     "port": 830,
# }

# payload = ""
# # # /data/routing/routing-instance[1]
# # payload = """
# #         <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
# #       <interface>
# #         <enabled>true</enabled>
# #       </interface>
# #     </interfaces>
# # """

# client = NetConfClient(config)
# result = client.get_filter(payload)
# print(result)