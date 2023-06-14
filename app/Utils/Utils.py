import collections

from config import logger as log
import yaml
from jinja2 import Template

from Models.GlobalParams import Global_params

from config import workflow_definition_files_path as path
import config
from config import settings

from typing import Tuple, Any, Optional, List

from github import Github

import os

def read_step_yaml(file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    log.debug(f"Reading read_step_yaml YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def read_workflow_steps(file_path: str, steps: List[Any], correlationID: str) -> Tuple[Optional[List[Any]], Optional[Exception]]:
    """This method will recursively read steps on the root  workflow YAML file, as well as child workflows.
    It will return a list of steps, or an error if one occurs.
    """
    try:
        
        global_params = Global_params().getMap(correlationID)
        log.debug(f"Global params:{global_params}")

        values_data = read_step_yaml(file_path.replace('.yml','.values.yml'))
        for key, value in values_data.items():
            global_params[key] = value

        log.debug(f"Global params:{global_params}")
        log.debug(f"Values file:\n{values_data}")
        
        log.debug(f"Reading file: {file_path}")
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        log.debug(f"Render the file content as a Jinja template")    
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
            step['workflow_name'] = renderedDict.get('name')
            step['workflow_metadata'] = renderedDict.get('metadata')
            step['workflow_dependencies'] = renderedDict.get('dependencies')
            step['correlationID'] = correlationID
                
            if step.get('type') == 'workflow':
                step['steps'] = []
                step['steps'], err = read_workflow_steps(f"{path}/{step.get('file')}", step['steps'], correlationID)
                # if err:
                #     return None, err
            else:
                step['type'] = "activity"
                step['config'] = read_step_yaml(f"{path}/{step['file']}")
                step['config']['correlationID'] = step['correlationID']
                step['config']['workflow_name'] = step['workflow_name']
                step['description'] = step['config']['description']
                step['milestoneStepName'] = step['config']['name']
                step['milestone'] = renderedDict.get('name')
                step['name'] = step['config']['name']
                
            log.debug(f"Adding step: {step}")
            steps.append(step)
        return steps, None
    except Exception as e:
        return None, e
    
def get_list_of_steps(file: str, correlationID: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"Getting list of steps from file {file}, path={path}, correlationID:{correlationID}")
    
    steps = []
    
    steps, error = read_workflow_steps(f"{path}/{file}", steps, correlationID)
    log.debug(f"steps:\n {steps}")
        
    if error:
        log.error(f"Error reading workflow file: {path}/{file}. error: {str(error)}")
        return None, error

    return steps, None
    # stepConfigs = []
    # for item in steps:
    #      if item.get('type') == 'workflow':
             
             
    #     config = read_step_yaml(f"{path}/{step['file']}")
    #     config['workflow_name'] = step['workflow_name']
    #     config['workflow_metadata'] = step['workflow_metadata']
    #     config['workflow_dependencies'] = step['workflow_dependencies']
    #     config['correlationID'] = step['correlationID']
    #     stepConfigs.append(config)

    # _ = [log.debug(stepConfig) for stepConfig in list(stepConfigs)]
    
    # return stepConfigs, 

def clone_step_yaml(repoName: str, branch: str, file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    # check if file exists locally, if not, read from repo and save locally
    if not os.path.exists(f"{path}/{file_path}"):
        g = Github(settings.repo_access_token)
        user = g.get_user()
        repository = user.get_repo(repoName)
        file_content = repository.get_contents(file_path, ref=branch).decoded_content.decode()
        log.info(file_content)
        with open(f"{path}/{file_path}", 'w') as f:
            f.write(file_content)
    return yaml.safe_load(file_content)
    
def clone_workflow_steps(repoName: str, branch: str, wfFileName: str, steps: List[Any], correlationID: str) -> Tuple[Optional[List[Any]], Optional[Exception]]:
    """This method will recursively read steps on the root  workflow YAML file, as well as child workflows.
    It will return a list of steps, or an error if one occurs.
    """
    try:
        
        global_params = Global_params().getMap(correlationID)
        log.debug(f"Global params:{global_params}")

        values_data = clone_step_yaml(wfFileName.replace('.yml','.values.yml'))
        for key, value in values_data.items():
            global_params[key] = value

        log.debug(f"Global params:{global_params}")
        log.debug(f"Values file:\n{values_data}")
        
        log.debug(f"Reading file: {wfFileName}")

        # TODO: add PyGithub code here to read the file from the repo
        # and to save it locally as well, comment out the code below after testing
        # with open(wfFileName, 'r') as f:
        #     file_content = f.read()
        
        # check if file exists locally, if not, read from repo and save locally
        if not os.path.exists(f"{path}/{wfFileName}"):
            g = Github(settings.repo_access_token)
            user = g.get_user()
            repository = user.get_repo(repoName)
            file_content = repository.get_contents(wfFileName, ref=branch).decoded_content.decode()
            log.info(file_content)
            with open(f"{path}/{wfFileName}", 'w') as f:
                f.write(file_content)
        
        log.debug(f"Render the file content as a Jinja template")    
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
            step['workflow_name'] = renderedDict.get('name')
            step['correlationID'] = correlationID
                
            if step.get('type') == 'workflow':
                step['steps'], err = clone_workflow_steps(repoName, branch, step.get('file'), step['steps'], correlationID)
                if err:
                    return None, err
            else:
                step['config'] = clone_step_yaml(step['file'])
                
            log.debug(f"Adding step: {step}")
            steps.append(step)
        return steps, None
    except Exception as e:
        return None, e

def clone_template(repoName: str, branch: str, wfFileName: str, requestId: str) -> Tuple[Optional[Any], Optional[Exception]]:
    log.debug(f"Getting list of steps from file {wfFileName}, path={path}")
    
    steps = []
    
    steps, error = clone_workflow_steps(repoName, branch, wfFileName,  steps, requestId)
    log.debug(f"steps:\n {steps}")
        
    if error:
        log.error(f"Error reading workflow file: {path}/{wfFileName}. error: {str(error)}")
        return None, error

    return steps, None