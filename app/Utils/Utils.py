import collections

from config import logger as log
import yaml
from jinja2 import Template

from Models.GlobalParams import Global_params

from config import workflow_definition_files_path as path
import config
from config import settings

from typing import Tuple, Any, Optional, List

from temporalio import workflow
with workflow.unsafe.imports_passed_through():
    from github import Github
    from github.GithubException import UnknownObjectException

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
    
    # return stepConfigs, None

def download_file(file_content, local_path):
    with open(local_path, 'wb') as f:
        f.write(file_content.decoded_content)

def save_path_recursively(repo, path, local_dir, branch):
    contents = repo.get_contents(path, ref=branch)

    for content in contents:
        log.debug(f"Fetching - {content.path}")
        if content.type == "dir":
            new_dir = os.path.join(local_dir, content.name)
            os.makedirs(new_dir, exist_ok=True)
            save_path_recursively(repo, content.path, new_dir, branch)
        else:
            local_path = os.path.join(local_dir, content.name)
            download_file(content, local_path)

errorMetadata = {
    421 : { "description" : "repo not found" },
    422 : { "description" : "branch not found" },
    423 : { "description" : "file not found" },
    900 : { "description" : "Generic error" },
}    

from dataclasses import dataclass

@dataclass
class CustomError:
    code: int = 900
    description: str = ''
    message: str = ''
    def __post_init__(self):
        self.description = errorMetadata[self.code]['description']
    def __str__(self):
        return f"Error code: {self.code}, description: {self.description}, message: {self.message}"
    def toJSON(self):
        return {
            "code": self.code,
            "description": self.description,
            "message": self.message
        }

def fetch_template_files(repoName: str, branch: str, wfFileName: str) -> Tuple[Optional[Any], Optional[CustomError]]:
    try:
        log.debug(f"Getting list of steps from file {wfFileName}, path={path}")
        g = Github(settings.repo_access_token)
        user = g.get_user()
        repo = user.get_repo(repoName)
        repoPath = wfFileName.split('/')[0]
        log.debug(f"repoPath: {repoPath}")
        local_dir = f"{path}/{repoPath}"
        log.debug(f"local_dir: {local_dir}")
        save_path_recursively(repo, repoPath, local_dir, branch)
        return "template files fetched successfully", None
    except UnknownObjectException as e:
        # generate error objects with codes and descriptions, this metadata will be maintained in a different file
        error = CustomError(code=421, message=str(e))
        log.error(f"Error fetching template files: {str(error)}")
        raise ValueError(error.toJSON())
    except Exception as e:
        error = CustomError(code=900, message=str(e))
        log.error(f"Error fetching template files: {str(error)}")
        raise ValueError(error.toJSON())

def get_value_from_dict_path(nested_dict, path):
    keys_list = path.split('.')
    temp = nested_dict
    for key in keys_list:
        if not isinstance(temp, dict):
            return None
        temp = temp.get(key, None)
        if temp is None:
            return None
    return temp

def get_value_from_dict_path_or_env(nested_dict, path, env_var_name):
    value = get_value_from_dict_path(nested_dict, path)
    if value is None:
        value = env_var_name
    return value