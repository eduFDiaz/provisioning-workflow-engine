from Consumer import KafkaConsumerSingleton
from Models.NotificationModel import NotificationModel
from config import logger as log
from config import settings

import asyncio
from pydantic import BaseModel

# uvicorn main:app --host 0.0.0.0 --port 4040 --reload

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from Clients.WebSocketManager import WebSocketManager as WSClient

app = FastAPI()

manager = WSClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    log.info("Waiting for Kafka to start up...")
    await asyncio.sleep(20)
    log.info("Starting Kafka Consumer...")
    app.kafka_consumer = KafkaConsumerSingleton.getInstance()
    await app.kafka_consumer.start_consuming(settings.kafka_topic, manager)
    
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # this will keep connections alive
            # Handle received data if necessary
            # to disconnect the client
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(client_id)

class Message(BaseModel):
    client_id: str
    message: str

@app.post("/milestone/")
async def send_message(message: NotificationModel):
    log.info(f"Received message: {message.toJSON()}")
    log.debug(f"active_connections: {manager.active_connections}")
    if manager.active_connections.get(str(message.requestID), None) is not None:
        await manager.send_message(str(message.requestID), message.toJSON())
    else:
        raise HTTPException(status_code=404, detail="Client not found")
    
from fastapi import HTTPException