import logging
from scrapli_netconf.driver import NetconfDriver
# Suppress the client logs only to CRITICAL only as
# it was bloating the log file with too much info
log = logging.getLogger('scrapli')
log.setLevel(logging.CRITICAL)

from Models.Errors.CustomNetconfStepError import CustomNetconfError

from config import logger as log

class NetConfClient:
    """A class to represent a NetConf Client"""
    def __init__(self, config):
        self.exceptionArgs = { 'host': config['host'],
                               'port': config['port'],
                               'username': str(config['auth_username'][:3] + '*' * (len(config['auth_username']) - 3)),
                               'password': str(config['auth_password'][:3] + '*' * (len(config['auth_password']) - 3))
                            }
        log.debug(f"NetConfClient self.exceptionArgs: {self.exceptionArgs}")
        self.device = config
        try:
            self.conn = NetconfDriver(**self.device)
            self.conn.open()
        except Exception as error:
            log.error(f"NetConfClient error: {error.__class__.__name__}")
            raise ValueError(CustomNetconfError(payload=error,args=self.exceptionArgs).toJSON())
    
    def __del__(self):
        log.critical("Closing NetConf connection")
        self.conn.close()

    def get_filter(self, payload):
        try:
            if payload == None or payload == "":
                # if no payload is provided, get the entire config
                result = self.conn.get_config(source="running")
            else:
                # if a payload is provided, get the config based on a subtree filter
                result = self.conn.get_config(filter_ = payload, filter_type="subtree", source="running")
            return result.result
        except Exception as error:
            log.error(f"NetConfClient error: {error.__class__.__name__}")
            self.exceptionArgs['payload'] = payload
            raise ValueError(CustomNetconfError(payload=error,args=self.exceptionArgs).toJSON())

    def edit_config(self, config):
        try:
            result = self.conn.edit_config(config=config, target="running")
            return result.result
        except Exception as error:
            log.error(f"NetConfClient error: {error.__class__.__name__}")
            self.exceptionArgs['config'] = config
            raise ValueError(CustomNetconfError(payload=error,args=self.exceptionArgs).toJSON())
    
    def commit(self):
        try:
            result = self.conn.commit()
            return result.result
        except Exception as error:
            raise ValueError(CustomNetconfError(payload=error,args=self.exceptionArgs).toJSON())

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