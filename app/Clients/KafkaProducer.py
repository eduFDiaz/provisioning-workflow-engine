from config import logger as log

from confluent_kafka import Producer
from threading import Lock

from Models.NotificationModel import NotificationModel
import uuid
from datetime import datetime

from config import logger as log
from typing import Dict
from config import settings

from config import settings
from Clients.CassandraConnection import CassandraConnection
from dao.NotificationDao import NotificationDao

kafka_config = {
    'bootstrap.servers': f"{settings.kafka_server}:{settings.kafka_port}",
}

class KafkaProducerSingleton(object):
    _instance = None
    _lock = Lock()

    def __init__(self, config):
        if KafkaProducerSingleton._instance is not None:
            raise Exception("This is a singleton class.")
        self.producer = Producer(config)

    @classmethod
    def get_instance(cls, server, port):
        kafka_config['bootstrap.servers'] = settings.kafka_server + ':' + settings.kafka_port
        log.info("kafka_config: {kafka_config}")
        with cls._lock:
            if cls._instance is None:
                cls._instance = KafkaProducerSingleton(kafka_config)
            return cls._instance

# Kafka Producer Singleton instance
async def get_kafka_producer(server, port):
    kafka_producer = KafkaProducerSingleton.get_instance(server, port)
    return kafka_producer.producer

def add_or_update_notification(message: Dict):
    log.info(f"notification_dict: {message}")
    notification = NotificationModel(**message)
    log.info(f"notification: {notification}")
    log.info(f"KafkaConsumerSingleton.add_or_update_notification({notification})")
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)
    notification_dao.add_or_update_notification(notification)
    return notification

async def send_notification(notification: NotificationModel) -> NotificationModel:
    log.debug(f"Sending notification: {notification.toJSON()}")
    add_or_update_notification(notification.__dict__)
    producer = (await get_kafka_producer(settings.kafka_server, settings.kafka_port))
    producer.produce(settings.kafka_topic, notification.toJSON())
    producer.flush()
    return notification

async def send_error_notification(notification: NotificationModel) -> NotificationModel:
    notification.status = "failed"
    notification.endTime = datetime.utcnow().strftime(settings.notification_date_format)
    log.debug(f"Notification Error: {notification.toJSON()}")
    await send_notification(notification)
    return notification

async def send_complete_notification(notification: NotificationModel) -> NotificationModel:
    notification.status = "completed"
    notification.endTime = datetime.utcnow().strftime(settings.notification_date_format)
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
    notification.startTime = datetime.utcnow().strftime(settings.notification_date_format)
    notification.endTime = ""
    log.debug(f"Notification In Progress: {notification.toJSON()}")
    await send_notification(notification)
    return notification