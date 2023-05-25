from Consumer import KafkaConsumerSingleton
from Models.NotificationModel import NotificationModel
from config import logger as log
import asyncio

import json
from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from typing import Dict

# uvicorn main:app --host 0.0.0.0 --port 4040 --reload

from fastapi import FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup():
    log.info("Waiting for Kafka to start up...")
    await asyncio.sleep(20)
    log.info("Starting Kafka Consumer...")
    app.kafka_consumer = KafkaConsumerSingleton.getInstance()
    app.kafka_consumer.start_consuming('test')

@app.post("/notification/")
async def get_notification(notification: NotificationModel):
    log.info(f"Received notification: {notification.toJSON()}")
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)
    fetchedNotification = notification_dao.get_notification(notification)
    log.info(f"fetchedNotification: {fetchedNotification}")
    return fetchedNotification