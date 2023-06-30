from Models.GlobalParams import Global_params

from typing import Union
from jinja2 import Template

from config import logger as log
from dataclasses import dataclass
from Models.Errors.CustomReadStepsTemplateError import CustomReadStepsTemplateError, READ_STEPS_TEMPLATE_ERRORS

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
        credentials = self.config.get('credentials')
        if credentials is None:
            log.error(f"credentials section not defined in yml file for step: {self.name}")
            raise ValueError(payload=CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_CREDENTIALS_NOT_DEFINED_ERROR, args={'stepName': self.name}).toJSON())
        if credentials.get('username') is None or credentials.get('password') is None:
            log.error(f"Missing username or password in {self.name} config")
            raise ValueError(payload=CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_USERNAME_OR_PASSWORD_NOT_DEFINED_ERROR, args={'stepName': self.name}).toJSON())
        self.username = self.replace_params(self.config['credentials']['username'])
        self.password = self.replace_params(self.config['credentials']['password'])
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
        log.error(f"Unsupported type: {type(param)}")
        raise ValueError(payload=CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_JINJA2_UNSOPPORTED_OBJECT_ERROR, args={'stepName': self.name}).toJSON())
    
@dataclass
class TemplateWorkflowArgs:
    requestId: str
    WorkflowFileName: str
    repoName: str
    branch: str
    