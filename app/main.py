# main.py
import asyncio

from Services.Workflows.WorkflowService import invoke_steps
from fastapi import FastAPI

from config import logger as log

import config

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials


from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from workflows.activities.activities import exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step
from temporal_worker import start_temporal_worker

users_db = {
    "admin": {
        "username": "admin",
        "password": "C1sco12345",
    }
}

app = FastAPI()
security = HTTPBasic()

@app.on_event("startup")
async def startup():
    log.info("Waiting for Temporal Worker to start up...")
    await asyncio.sleep(20)
    await start_temporal_worker(config.temporal_url,
                                config.temporal_namespace,
                                config.temporal_queue_name, 
                                [ExecuteRestTask,
                                 ExecuteCliTask,
                                 ExecuteNetConfTask,
                                 ExecuteGrpcTask], 
                                [exec_rest_step,
                                 exec_cli_step,
                                 exec_netconf_step,
                                 exec_grpc_step])

@app.on_event("shutdown")
async def shutdown():
    log.info("Shutting down Temporal Worker...")
    await config.temporal_worker.stop()
    
@app.post("/execute_workflow/",
         summary="this API will execute a temporal workflow from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def execute_workflow() -> HTMLResponse:
    try:
        res = (await invoke_steps("phy_interface_vrf.yml"))
        return HTMLResponse(content=f"Workflow executed successfully {res}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    

def getConfig(orderId: str):
    log.info(f"getConfig {orderId}")
    try:
        configs = {}
        configs["VNS_2358258"] ={
            "vrf": [
                {
                    "name": "VRF_Capgemini",
                    "rd": "100:110",
                    "rt-import": [
                        "100:1000"
                    ],
                    "rt-export": [
                        "100:1000"
                    ],
                    "ipv4-import": [
                        "Capgemini-VRF-IMPORT"
                    ],
                    "ipv4-export": [
                        "Capgemini-VRF-EXPORT"
                    ]
                }
            ],
            "route-map": [
                {
                    "name": "Capgemini-VRF-IMPORT",
                    "match-list": [
                        {
                            "index": 10,
                            "operation" : "permit",
                            "prefix": "Capgemini-DC1-Management"
                        },
                        {
                            "index": 20,
                            "operation" : "permit",
                            "prefix": "Capgemini-DC2-Management"
                        }
                    ]
                }
            ],
            "ip-prefix-list": [
                {
                    "name": "Capgemini-DC1-Management",
                    "index": 10,
                    "action": "permit",
                    "prefix": "192.168.187.0/28"
                }
            ],
        }
        return configs[orderId]
    except Exception as e:
        log.error(f"Error: {e}")
        return f"Error: {e}"
    
def authorize(security: HTTPBasicCredentials = Depends(security)):
    if security.username in users_db:
        if security.password == users_db[security.username]["password"]:
            return True
    return False

@app.get("/config/{orderId}",
        summary="this API will return the config for the given orderId",
        description="this API will return the config for the given orderId"
        ,dependencies=[Depends(authorize)])
async def get_config(orderId: str) -> JSONResponse:
    try:
        config = getConfig(orderId)
        return JSONResponse(content=config, status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return JSONResponse(content=f"Error: {e}", status_code=500)