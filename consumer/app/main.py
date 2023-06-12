from Consumer import KafkaConsumerSingleton
from Models.NotificationModel import NotificationModel
from config import logger as log
import asyncio
from pydantic import BaseModel

from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from typing import Dict
import uuid

# uvicorn main:app --host 0.0.0.0 --port 4040 --reload

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

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
    # await asyncio.sleep(20)
    log.info("Starting Kafka Consumer...")
    app.kafka_consumer = KafkaConsumerSingleton.getInstance()
    await app.kafka_consumer.start_consuming('test', manager)

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
async def get_notification_by_correlationID(correlationID: str):
    log.info(f"get_notification_by_correlationID: {correlationID}")
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)
    notificationsbyCorrelationId = notification_dao.get_notifications_by_correlationID(uuid.UUID(correlationID))
    log.info(f"fetchedNotification: {notificationsbyCorrelationId}")
    if len(notificationsbyCorrelationId) == 0:
        return JSONResponse(content=[], status_code=202)
    if len(notificationsbyCorrelationId) != 0:
        return notificationsbyCorrelationId
    
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
    # await asyncio.create_task(manager.keep_alive(client_id))
    # try:
    #     while True:
    #         # data = await websocket.receive_text()
    #         pass
    # except WebSocketDisconnect:
    #     await manager.disconnect(client_id)

class Message(BaseModel):
    client_id: str
    message: str

@app.post("/milestone/")
async def send_message(message: NotificationModel):
    log.info(f"Received message: {message.toJSON()}")
    log.debug(f"active_connections: {manager.active_connections}")
    if manager.active_connections.get(str(message.correlationID), None) is not None:
        await manager.send_message(str(message.correlationID), message.toJSON())
    else:
        raise HTTPException(status_code=404, detail="Client not found")
    
from fastapi import HTTPException