# main.py
import asyncio
from Services.prime_service import invokePrimeWorkflow
from Services.factorial_service import invokeFactorialWorkflow
from Services.prime_factorial_service import invokePrimeFactorialWorkflow
from Services.Workflows.WorkflowService import invoke_steps
from fastapi import FastAPI, HTTPException, File, UploadFile
from typing import List
import os

from config import logger as log

import config

from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, File, UploadFile

from activities import find_factorial_activity, find_prime
from Models.RestStep import exec_rest_step
from Models.CliStep import exec_cli_step
from Models.NetConfStep import exec_netconf_step
from Models.GrpcStep import exec_grpc_step
from workflows.prime_workflow import FindPrimeFlow
from workflows.prime_factorial_workflow import PrimeFactorialFlow
from workflows.factorial_workflow import FactorialFlow
from workflows.ExecuteStepsFlow import ExecuteRestTask
from temporal_worker import start_temporal_worker

app = FastAPI()

@app.on_event("startup")
async def startup():
    log.info("Waiting for Temporal Worker to start up...")
    await asyncio.sleep(20)
    await start_temporal_worker(config.temporal_url,
                                config.temporal_namespace,
                                config.temporal_queue_name, 
                                [FindPrimeFlow,
                                 FactorialFlow,
                                 PrimeFactorialFlow,
                                 ExecuteRestTask], 
                                [find_prime,
                                 find_factorial_activity,
                                 exec_rest_step,
                                 exec_cli_step,
                                 exec_netconf_step,
                                 exec_grpc_step])

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_client.close()

@app.get("/invokePrimeFlow/{number}",
         summary="invoke Prime Flow", 
         description="Find the Nth prime number Ex: 5 returns 11, 10 returns 29, 100 returns 541")
async def invokePrimeFlow(number: int):
    log.info(f"invokePrimeFlow {number}")
    try:
        prime = await invokePrimeWorkflow(number)
        log.debug(f"Prime: {prime}")
        return HTMLResponse(content=f"Prime: {prime}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)

@app.get("/invokeFactorialFlow/{number}",
         summary="invoke Factorial Flow", 
         description="Find f(n) = (n)! Ex: 5 returns 120, 10 returns 3628800, 100 returns 9.33262154439441e+157")
async def invokeFactorialFlow(number: int):
    log.info(f"invokeFactorialFlow {number}")
    try:
        n = await invokeFactorialWorkflow(number)
        log.debug(f"Factorial: {n}")
        return HTMLResponse(content=f"Factorial: {n}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    
@app.get("/invokePrimeFactorialFlow/{number}",
         summary="invoke Prime Factorial Flow", 
         description="Find the nth prime number and then find the factorial of that number, Ex: 10th prime = 29, 29! = 8.84176199E30")
async def invokePrimeFactorialFlow(number: int):
    log.info(f"invokePrimeFactorialFlow {number}")
    try:
        n = await invokePrimeFactorialWorkflow(number)
        log.debug(f"invokePrimeFactorialWorkflow: {n}")
        return HTMLResponse(content=f"invokePrimeFactorialFlow: {n}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)
    
@app.post("/execute_workflow/",
         summary="this API will execute a temporal workflow from a YAML file", 
         description="The workflow yaml file will have declaration of the steps and embedded jinja templates")
async def execute_workflow() -> HTMLResponse:
    try:
        n = await invoke_steps()
        return HTMLResponse(content=f"Workflow executed successfully {n}", status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)