# main.py
import asyncio

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials


from config import logger as log

import config

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
    log.info("Waiting for config_ms app to startup...")

@app.on_event("shutdown")
async def shutdown():
    log.info("Shutting down config_ms...")

def getConfig(requestID: str):
    log.info(f"getConfig {requestID}")
    try:
        configs = {}
        configs["changing-this-to-any-id"] ={
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
                },
                {
                    "name": "Capgemini-DC2-Management",
                    "index": 20,
                    "action": "permit",
                    "prefix": "192.168.187.0/28"
                }
            ],
        }
        return configs['changing-this-to-any-id']
    except Exception as e:
        log.error(f"Error: {e}")
        return f"Error: {e}"
    
def authorize(security: HTTPBasicCredentials = Depends(security)):
    if security.username in users_db:
        if security.password == users_db[security.username]["password"]:
            return True
    return False

@app.get("/config/{correlationID}",
        summary="this API will return the config for the given correlationID",
        description="this API will return the config for the given correlationID"
        ,dependencies=[Depends(authorize)])
async def get_config(correlationID: str) -> JSONResponse:
    try:
        config = getConfig(correlationID)
        return JSONResponse(content=config, status_code=200)
    except Exception as e:
        log.error(f"Error: {e}")
        return JSONResponse(content=f"Error: {e}", status_code=500)