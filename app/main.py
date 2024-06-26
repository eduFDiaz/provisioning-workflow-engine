# main.py
import asyncio
import uuid
from datetime import timedelta

from Services.Workflows.WorkflowService import get_steps_configs, TemplateWorkflowArgs, TemplateWorkflow, TemplateChildWorkflow, RunTasks, run_TemplateWorkFlow, workflowStatus, get_last_error
from Models.NotificationModel import NotificationModel

from config import logger as log
from config import settings
import config

from typing import Optional


from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Depends, FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from Clients.KafkaProducer import get_kafka_producer

from Clients.CassandraConnection import CassandraConnection
from dao.NotificationDao import NotificationDao

from workflows.ExecuteStepsFlow import ExecuteRestTask, ExecuteCliTask, ExecuteNetConfTask, ExecuteGrpcTask
from workflows.activities.activities import read_template, clone_template, exec_rest_step, exec_cli_step, exec_netconf_step, exec_grpc_step


from temporal_worker import start_temporal_worker
from temporalClient import TemporalClient

import asyncio
import concurrent.futures
import threading

from temporalio.exceptions import ApplicationError, ActivityError
from temporalio.client import WorkflowFailureError

from dao.ErrorDao import ErrorDao

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
    expose_headers=["*"],
)
security = HTTPBasic()

@app.on_event("startup")
async def startup():
    log.info("Waiting for Temporal Worker to start up...")
    # await asyncio.sleep(30)
    await start_temporal_worker(settings.temporal_server,
                                settings.temporal_namespace,
                                settings.temporal_queuename,
                                [TemplateWorkflow,
                                 TemplateChildWorkflow,
                                 ExecuteRestTask,
                                 ExecuteCliTask,
                                 ExecuteNetConfTask,
                                 ExecuteGrpcTask], 
                                [read_template,
                                 clone_template,
                                 exec_rest_step,
                                 exec_cli_step,
                                 exec_netconf_step,
                                 exec_grpc_step])
    
    app.kafka_producer = (await get_kafka_producer())
    log.info("Temporal Worker and Kafka Producer started successfully.")

@app.on_event("shutdown")
async def shutdown():
    log.info("Shutting down Temporal Worker...")
    await config.temporal_worker.stop()

def run_in_new_thread(loop, coro):
    asyncio.run_coroutine_threadsafe(coro, loop)
    
@app.post("/execute_workflow/",
         summary="this API will execute a temporal workflow from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def execute_workflow(request_id: Optional[str] = Header(None),
                           flowFileName: str = Header(...),
                           repoName: str = Header(...),
                           branch: str = Header(...)) -> JSONResponse:
    log.debug(f"POST API: execute_workflow/?flowFileName={flowFileName}, request_id={request_id}")
    try:
        should_invoke_steps = False
        if not request_id:
            log.info("request_id not found in header")
            request_id = str(uuid.uuid4())
            
        connection = CassandraConnection()
        session = connection.get_session()
        notification_dao = NotificationDao(session)
        
        log.debug(f"fetching milestones for requestID: {request_id}")
        milestones = notification_dao.get_notifications_by_correlationID(uuid.UUID(request_id))

        log.info(f"milestones: {milestones} for requestID: {request_id}")

        # this is the trivial case where there are no milestones in db for this requestID
        if len(milestones) == 0:
            log.info("no milestones found in db for this requestID")
            should_invoke_steps = True
        else:
            milestonesInProgress = [NotificationModel for milestone in milestones if milestone.status == "in-progress"]  
            milestonesFailed = [NotificationModel for milestone in milestones if milestone.status == "failed"]
            milestonesCompleted = [NotificationModel for milestone in milestones if milestone.status == "completed"]
            milestonesNotStarted = [NotificationModel for milestone in milestones if milestone.status == "not-started"]

            # log all the milestones by status
            log.info(f"milestonesInProgress: {milestonesInProgress} - {len(milestonesInProgress)}")
            log.info(f"milestonesFailed: {milestonesFailed} - {len(milestonesFailed)}")
            log.info(f"milestonesCompleted: {milestonesCompleted} - {len(milestonesCompleted)}")
            log.info(f"milestonesNotStarted: {milestonesNotStarted} - {len(milestonesNotStarted)}")

            if len(milestonesInProgress) > 0:
                # this means that some milestones are in progress
                should_invoke_steps = False
            
            if len(milestonesFailed) > 0:
                # this means that some milestones have failed
                should_invoke_steps = True
            
            if len(milestonesNotStarted) == len(milestones):
                # this means that no milestones have started
                should_invoke_steps = True

            if len(milestonesCompleted) == len(milestones):
                # this means that all milestones have completed
                should_invoke_steps = False
            
            if (len(milestonesCompleted) != len(milestonesInProgress) and len(milestonesCompleted) != len(milestonesNotStarted)) and (len(milestonesInProgress) == 0 != len(milestonesFailed) == 0):
                # this means that some milestones are in progress and some have completed
                should_invoke_steps = True
        
        log.info(f"should_invoke_steps final value: {should_invoke_steps} - flowFileName {flowFileName} - requestID: {request_id}")
        if should_invoke_steps is True:
            # invoke_steps on a separate thread
            taskList = {}
            
            try:
                # run_TemplateWorkFlow will run synchronously (clone_template, read_template)
                result = await (run_TemplateWorkFlow(flowFileName, request_id, repoName, branch))
                taskList = result
            except WorkflowFailureError as err:
                log.debug(f"Workflow failed with error: {err}")
                error = await get_last_error(request_id=request_id)
                return JSONResponse(str(error.error), status_code=500)

            # if code reaches here, it means that cloning and reading templates was successful
            loop = asyncio.get_event_loop()
            threading.Thread(target=run_in_new_thread, args=(loop, RunTasks(taskList))).start()

        response = JSONResponse(content={"request-id": request_id}, status_code=202)
        return response
    except Exception as e:
        log.error(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/workflow_status/",
         summary="this API will return the status of the workflow", 
         description="status: in-progress, completed, not-started or failed, along with the last error in case of failed")
async def workflow_status(request_id: str = Header(...),
                          workflowFileName: str = Header(...)) -> JSONResponse:
    log.debug(f"GET API: workflow_status request_id: {request_id}")
    return (await workflowStatus(request_id=request_id, workflowFileName=workflowFileName))
    
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
    app.kafka_producer.produce(settings.kafka_topic, payload.toJSON())
    app.kafka_producer.flush()
    return {"message": f"Message sent to Kafka {payload.toJSON()}"}

@app.post("/notification/")
async def get_notification(notification: NotificationModel):
    log.info(f"Received notification: {notification.toJSON()}")
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)
    fetchedNotification = notification_dao.get_notification(notification)
    log.info(f"fetchedNotification: {fetchedNotification}")
    return fetchedNotification

@app.get("/notification/")
async def get_notification_by_correlationID(requestID: str):
    log.info(f"get_notification_by_correlationID: {requestID}")
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)
    notificationsbyCorrelationId = notification_dao.get_notifications_by_correlationID(uuid.UUID(requestID))
    log.info(f"fetchedNotification: {notificationsbyCorrelationId}")
    if len(notificationsbyCorrelationId) == 0:
        return JSONResponse(content=[], status_code=202)
    if len(notificationsbyCorrelationId) != 0:
        return notificationsbyCorrelationId

@app.get("/fetch_flow_steps/",
         summary="this API will fetch workflow steps including child workflows from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def fetch_steps(workflowFileName: str, requestID: str):   
    try:
        log.info(f"fetch_steps {workflowFileName}, requestID - {requestID}")
        res = (await get_steps_configs(workflowFileName, requestID))
        return JSONResponse(content=res, status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return JSONResponse(content=e, status_code=500)

@app.get("/errors/")
async def get_errors_by_requestID(requestID: str):
    log.info(f"get_errors_by_requestID: {requestID}")
    connection = CassandraConnection()
    session = connection.get_session()
    error_dao = ErrorDao(session)
    errorsbyRequestID = error_dao.get_errors_by_correlationID(uuid.UUID(requestID))
    log.info(f"errorsbyRequestID: {errorsbyRequestID}")
    if len(errorsbyRequestID) == 0:
        return JSONResponse(content=[], status_code=202)
    if len(errorsbyRequestID) != 0:
        return errorsbyRequestID