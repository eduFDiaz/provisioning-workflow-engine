from Models.GlobalParams import Global_params
from config import api_credentials

from typing import Union
from jinja2 import Template

from config import logger as log

class Process:
    """Base class for all process types"""
    def __init__(self, config):
        self.global_params = Global_params().getMap(config['correlationID'])
        self.name = config['name']
        self.configType = config['configType']
        self.config = config
        self.set_credentials()
    def process_step(self) -> int:
        """This method will be implemented by the child Step classes
        It will be used to execute the process, REST, CLI, NETCONF, etc"""
        raise NotImplementedError
    def validate_process(self):
        """This method will be implemented by the child classes"""
        raise NotImplementedError
    def render_jinja_template(self):
        """This method will be implemented by the child classes"""
        raise NotImplementedError
    def set_credentials(self):
        if self.configType not in api_credentials:
            log.error(f"Unsupported configType: {self.configType}")
            raise ValueError(f"Unsupported configType: {self.configType}")
        self.username = api_credentials[self.configType]['username']
        self.password = api_credentials[self.configType]['password']
    def replace_params(self, param: Union[str, dict]) -> Union[str, dict]:
        """ This method will replace all the jinja2 template variables with the values from the params file
        it will also replace header placeholders with the values from the global_params dictionary"""
        log.debug(f"template params -> global {self.global_params}")
        log.debug(f"{self.configType} before replace_params\n{param} - type: {type(param)}")
        if isinstance(param, str):
            template = Template(param, trim_blocks=True, lstrip_blocks=True)
            renderedParam = template.render(**self.global_params)
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        elif isinstance(param, dict):
            renderedParam = {}
            for key, value in param.items():
                renderedParam[key] = self.replace_params(value)
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        raise ValueError(f"Unsupported type: {type(param)}")