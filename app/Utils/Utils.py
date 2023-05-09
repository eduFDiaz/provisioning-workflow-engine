import collections
from config import logger as log
import yaml

def read_yaml(file_path) -> collections.OrderedDict:
    """This function will read a YAML file and return an OrderedDict
    will be used to read configs and steps files"""
    log.debug(f"Reading YAML file: {file_path}")
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)