from pydantic import BaseModel
import json

class NotificationModel(BaseModel):
    workflow: str
    status: str
    step: str
    milestoneName: str
    milestoneStepName: str
    startTime: str
    endTime: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
