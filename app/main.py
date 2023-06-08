# main.py
import asyncio

from Services.Workflows.WorkflowService import invoke_steps, get_steps_configs
from Models.NotificationModel import NotificationModel

from config import logger as log

import config

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from Clients.KafkaProducer import get_kafka_producer

from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from workflows.activities.activities import exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step
from temporal_worker import start_temporal_worker

from jproperties import Properties

users_db = {
    "admin": {
        "username": "admin",
        "password": "C1sco12345",
    }
}





app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBasic()



@app.on_event("startup")
async def startup():
    configs = Properties()
    with open('app.properties', 'rb') as config_file:
        configs.load(config_file)

    log.info("Waiting for Temporal Worker to start up...")
    # await asyncio.sleep(30)
    await start_temporal_worker(configs.get("temporal.server").data,
                                configs.get("temporal.namespace").data,
                                configs.get("temporal.queuename").data,
                                [ExecuteRestTask,
                                 ExecuteCliTask,
                                 ExecuteNetConfTask,
                                 ExecuteGrpcTask], 
                                [exec_rest_step,
                                 exec_cli_step,
                                 exec_netconf_step,
                                 exec_grpc_step])
    
    app.kafka_producer = (await get_kafka_producer(configs.get("kafka.server").data, configs.get("kafka.port").data))

@app.on_event("shutdown")
async def shutdown():
    log.info("Shutting down Temporal Worker...")
    await config.temporal_worker.stop()
    
@app.post("/execute_workflow/",
         summary="this API will execute a temporal workflow from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def execute_workflow(flowFileName: str) -> HTMLResponse:
    try:
        res = (await invoke_steps(flowFileName))
        return HTMLResponse(content=f"Workflow executed successfully {res}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)

@app.get("/fetch_flow_steps/",
         summary="this API will fetch workflow steps including child workflows from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def fetch_steps(workflowFileName: str, correlationId: str):   
    try:
        res, err = (await get_steps_configs(workflowFileName, correlationId))
        if err:
            return JSONResponse(content=err, status_code=500)
        else:
            return JSONResponse(content=res, status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    
def authorize(security: HTTPBasicCredentials = Depends(security)):
    if security.username in users_db:
        if security.password == users_db[security.username]["password"]:
            return True
    return False

@app.post("/kafka/",
         summary="this API will send a message to Kafka", 
         description="The payload will be sent to Kafka")
async def kafka_endpoint(payload: NotificationModel) -> JSONResponse:
    # Send payload to kafka using test topic
    log.info(f"Sending payload to Kafka: {payload.toJSON()}")
    app.kafka_producer.produce('test', payload.toJSON())
    app.kafka_producer.flush()
    return {"message": f"Message sent to Kafka {payload.toJSON()}"}