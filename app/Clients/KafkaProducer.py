from config import is_running_in_docker
from config import logger as log

from confluent_kafka import Producer
from threading import Lock

from Models.GlobalParams import Global_params
from Models.NotificationModel import NotificationModel
import uuid
from datetime import datetime

from config import logger as log
from typing import Dict

global_params = Global_params()

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
}

class KafkaProducerSingleton(object):
    _instance = None
    _lock = Lock()

    def __init__(self, config):
        if KafkaProducerSingleton._instance is not None:
            raise Exception("This is a singleton class.")
        self.producer = Producer(config)

    @classmethod
    def get_instance(cls):
        if is_running_in_docker():
            KAFKA_URL = 'kafka:9092'
        else:
            KAFKA_URL = 'localhost:9092'
        kafka_config['bootstrap.servers'] = KAFKA_URL
        log.info(f"kafka_config: {kafka_config}")
        with cls._lock:
            if cls._instance is None:
                cls._instance = KafkaProducerSingleton(kafka_config)
            return cls._instance

# Kafka Producer Singleton instance
async def get_kafka_producer():
    kafka_producer = KafkaProducerSingleton.get_instance()
    return kafka_producer.producer

async def send_notification(notification: NotificationModel) -> NotificationModel:
    log.debug(f"Sending notification: {notification.toJSON()}")
    producer = (await get_kafka_producer())
    producer.produce('test', notification.toJSON())
    producer.flush()
    return notification

async def send_error_notification(notification: NotificationModel) -> NotificationModel:
    notification.status = "failed"
    notification.endTime = datetime.utcnow().strftime("%Y-%m-%d UTC %H:%M:%S")
    log.debug(f"Notification Error: {notification.toJSON()}")
    await send_notification(notification)
    return notification

async def send_complete_notification(notification: NotificationModel) -> NotificationModel:
    notification.status = "completed"
    notification.endTime = datetime.utcnow().strftime("%Y-%m-%d UTC %H:%M:%S")
    log.debug(f"Notification Completed: {notification.toJSON()}")
    await send_notification(notification)
    return notification

def prepare_notification(conf: Dict) -> NotificationModel:
    notification = NotificationModel(
        correlationID=uuid.UUID(conf['correlationID']),
        workflow=conf['workflow_name'],
        status="in-progress",
        step=conf['name'],
        milestoneName=conf.get('milestoneName', conf['workflow_name']),
        milestoneStepName = conf.get('milestoneStepName', conf['name']),
        startTime = "",
        endTime = ""
    )
    log.debug(f"Prepare Notification: {notification.toJSON()}")
    return notification

async def send_in_progress_notification(notification: NotificationModel) -> NotificationModel:
    notification.status="in-progress"
    notification.startTime = datetime.utcnow().strftime("%Y-%m-%d UTC %H:%M:%S")
    notification.endTime = ""
    log.debug(f"Notification In Progress: {notification.toJSON()}")
    await send_notification(notification)
    return notification