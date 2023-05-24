import yaml
from pydantic import BaseModel
import json
import uuid
from typing import Literal

with open('models_metadata.yaml', 'r') as f:
    models_metadata = yaml.safe_load(f)
    print(models_metadata)
    status_enum_values = tuple(models_metadata['NotificationModel']['properties']['status'])

    class NotificationModel(BaseModel):
        correlationId: uuid.UUID
        workflow: str
        status: Literal[status_enum_values]
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

# new_notification = NotificationModel(
#     correlationId=uuid.UUID("951ee60f-bceb-49bd-ad85-cd85ec1d8595"),
#     workflow="workflow1", 
#     status="completed", 
#     step="step1", 
#     milestoneName="milestoneName1", 
#     milestoneStepName="milestoneStepName1", 
#     startTime="startTime1", 
#     endTime="endTime1"
# )

# print(new_notification.toJSON())