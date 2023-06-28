from dataclasses import dataclass

from typing import Any, Dict

@dataclass
class CustomErrorBase:
    payload: Any
    args: Dict[str, Any]
    code: str = "999"
    description: str = ''
    message: str = ''
    def __post_init__(self):
        pass
    def __str__(self):
        return f"Error code: {self.code}, description: {self.description}, message: {self.message}"
    def toJSON(self):
        return {
            "code": self.code,
            "description": self.description,
            "message": self.message
        }