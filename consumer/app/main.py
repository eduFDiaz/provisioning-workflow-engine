from Consumer import KafkaConsumerSingleton
from config import logger as log
import asyncio

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

@app.get("/")
async def read_root():
    return {"Hello": "World"}