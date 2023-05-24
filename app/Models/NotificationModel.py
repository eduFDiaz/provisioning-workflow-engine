from pydantic import BaseModel
from typing import Literal
import json
import uuid

from enum import Enum
import yaml

class StatusEnum(str, Enum):
    completed = "completed"
    failed = "failed"
    in_progress = "in-progress"

class NotificationModel(BaseModel):
    correlationId: uuid.UUID
    workflow: str
    status: StatusEnum
    step: str
    milestoneName: str
    milestoneStepName: str
    startTime: str
    endTime: str

    def toJSON(self):
        json_dict = self.dict()
        json_dict['correlationId'] = str(json_dict['correlationId'])
        return json.dumps(json_dict, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
