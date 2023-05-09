from config import api_credentials, Global_params
from Utils.Utils import read_yaml

from typing import Optional, Union
from jinja2 import Environment, Template, FileSystemLoader

from config import logger as log

global_params = Global_params()

import json

from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Process:
    """Base class for all process types"""
    config: Dict
    name: str = field(init=False)
    configType: str = field(init=False)
    templateParams: Dict = field(init=False)
    username: str = field(init=False)
    password: str = field(init=False)

    def __init__(self, config: Dict):
        self.config = config
        self.name = self.config['name']
        self.configType = self.config['configType']
        self.set_credentials()
        self.templateParams = read_yaml(api_credentials[self.configType]['paramsFile'])
        global_params.update(self.templateParams)

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
        log.debug(f"template params -> global {global_params}")
        log.debug(f"{self.configType} before replace_params\n{param} - type: {type(param)}")
        if isinstance(param, str):
            template = Template(param, trim_blocks=True, lstrip_blocks=True)
            renderedParam = template.render(**global_params.getMap())
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        elif isinstance(param, dict):
            renderedParam = {}
            for key, value in param.items():
                renderedParam[key] = self.replace_params(value)
            log.debug(f"{self.configType} after replace_params\n{renderedParam}")
            return renderedParam
        raise ValueError(f"Unsupported type: {type(param)}")