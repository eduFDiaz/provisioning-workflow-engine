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