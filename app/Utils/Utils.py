import collections

from config import logger as log
import yaml
from jinja2 import Template

from Models.GlobalParams import Global_params

from config import workflow_definition_files_path as path
import config

from typing import Tuple, Any, Optional, List

def read_step_yaml(file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    log.debug(f"Reading read_step_yaml YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def read_workflow_steps(file_path: str, steps: List[Any], requestID: str) -> Tuple[Optional[List[Any]], Optional[Exception]]:
    """This method will recursively read steps on the root  workflow YAML file, as well as child workflows.
    It will return a list of steps, or an error if one occurs.
    """
    log.debug(f"Reading read_flow_yaml YAML file: {file_path}")
    try:
        
        global_params = Global_params().getMap(requestID)
        log.debug(f"Global params:\n{global_params}")

        values_data = read_step_yaml(file_path.replace('.yml','.values.yml'))
        
        for key, value in values_data.items():
            global_params[key] = value

        log.debug(f"Values file:\n{values_data}")
        with open(file_path, 'r') as f:
            file_content = f.read()
            
        # Render the file content as a Jinja template
        template = Template(file_content)
        rendered_template = template.render(**global_params)

        log.debug(f"Jinja template:\n{file_content}")
        log.debug(f"Rendered YAML file:\n{rendered_template}")

        # Load the rendered template as a YAML
        renderedDict = yaml.safe_load(rendered_template)

        log.debug(f"Rendered YAML file dict:\n{renderedDict}")
        
        # root workflow should be a list of steps (i.e renderedDict.get('steps')==True)
        for step in renderedDict['steps']:
            log.debug(f"Found step: {step.get('name')}")
            if step.get('type') == 'workflow':
                steps, err = read_workflow_steps(f"{path}/{step.get('file')}", steps, requestID)
                # if err:
                #     return None, err
            else:
                step['workflow_name'] = renderedDict.get('name')
                step['workflow_metadata'] = renderedDict.get('metadata')
                step['workflow_dependencies'] = renderedDict.get('dependencies')
                step['requestID'] = requestID
                log.debug(f"Adding step: {step}")
                steps.append(step)
        return steps, None
    except Exception as e:
        return None, e
    
async def get_list_of_steps(file: str, requestID: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"Getting list of steps")
    
    steps = []
    
    steps, error = read_workflow_steps(f"{path}/{file}", steps, requestID)
    
    if error:
        log.error(f"Error reading workflow file: {file}")
        return None, error

    stepConfigs = []
    for step in steps:
        config = read_step_yaml(f"{path}/{step['file']}")
        config['workflow_name'] = step['workflow_name']
        config['workflow_metadata'] = step['workflow_metadata']
        config['workflow_dependencies'] = step['workflow_dependencies']
        config['requestID'] = step['requestID']
        stepConfigs.append(config)

    _ = [log.debug(stepConfig) for stepConfig in list(stepConfigs)]
    
    return stepConfigs, None