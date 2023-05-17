import collections
from config import logger as log
import yaml
from jinja2 import Template
from Models.GlobalParams import Global_params

global_params = Global_params()

def read_step_yaml(file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    log.debug(f"Reading read_step_yaml YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def read_flow_yaml(file_path: str) -> collections.OrderedDict:
    """This function will read a YAML file, render it as a Jinja template,
    and return an OrderedDict. It will be used to read configs and steps files."""
    log.debug(f"Reading read_flow_yaml YAML file: {file_path}")

    values_data = read_step_yaml(file_path.replace('.yml','.values.yml'))
    
    for key, value in values_data.items():
        global_params.setitem(key, value)

    log.debug(f"Global params:\n{global_params.getMap()}")

    log.debug(f"Values file:\n{values_data}")
    with open(file_path, 'r') as f:
        file_content = f.read()
        
    # Render the file content as a Jinja template
    template = Template(file_content)
    rendered_template = template.render(**global_params.getMap())

    log.debug(f"Jinja template:\n{file_content}")
    log.debug(f"Rendered YAML file:\n{rendered_template}")

    # Load the rendered template as a YAML
    return yaml.safe_load(rendered_template)