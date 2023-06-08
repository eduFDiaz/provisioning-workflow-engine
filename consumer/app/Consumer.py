from confluent_kafka import Consumer, KafkaException
import threading
from Models.NotificationModel import NotificationModel
from config import logger as log
from config import is_running_in_docker
import json
from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from typing import Dict

from Clients.WebSocketManager import WebSocketManager as WSClient

import asyncio

manager = WSClient()

# docker exec -it kafka bash
# kafka-console-consumer --bootstrap-server kafka:9092 --topic test --from-beginning
# [appuser@0586aeb882ba ~]$ kafka-console-consumer --bootstrap-server kafka:9092 --topic test --from-beginning
# workflow='string2' status='string2' step='string' milestoneName='string' milestoneStepName='string' startTime='string' endTime='string'
# workflow='string2' status='string2' step='string' milestoneName='string' milestoneStepName='string' startTime='string' endTime='string'
# workflow='string2' status='string2' step='string' milestoneName='string' milestoneStepName='string' startTime='string' endTime='string'

kafka_config = {
                'bootstrap.servers': 'kafka:9092',
                'group.id': 'my-group',
                'auto.offset.reset': 'earliest'
            }

class KafkaConsumerSingleton(object):
    _instance = None
    _lock = threading.Lock()
    
    @staticmethod
    def getInstance():
        log.info("KafkaConsumerSingleton.getInstance()")
        with KafkaConsumerSingleton._lock:
            if KafkaConsumerSingleton._instance == None:
                KafkaConsumerSingleton._instance = KafkaConsumerSingleton()
            return KafkaConsumerSingleton._instance

    def __init__(self):
        try:
            if self._instance != None:
                raise Exception("This class is a singleton!")
            else:
                if is_running_in_docker():
                    KAFKA_URL = 'kafka:9092'
                else:
                    KAFKA_URL = 'localhost:9092'
                kafka_config['bootstrap.servers'] = KAFKA_URL
                log.info(f"kafka_config: {kafka_config}")
                self._instance = Consumer(kafka_config)
        except Exception as e:
            log.error(f"KafkaConsumerSingleton.__init__(): {e}")
    
    def add_or_update_notification(self, message: Dict):
        log.info(f"notification_dict: {message}")
        notification = NotificationModel(**message)
        log.info(f"notification: {notification}")
        log.info(f"KafkaConsumerSingleton.add_or_update_notification({notification})")
        connection = CassandraConnection()
        session = connection.get_session()
        notification_dao = NotificationDao(session)
        notification_dao.add_or_update_notification(notification)
        return notification

    async def start_consuming(self, topic, manager: WSClient):
        log.info(f"KafkaConsumerSingleton.start_consuming({topic})")
        self._instance.subscribe([topic])

        async def _consume():
            while True:
                msg = self._instance.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    log.error(f"Consumer error: {msg.error()}")
                    raise KafkaException(msg.error())
                else:
                    # Here you can do whatever you want with the messages.
                    log.debug(f"Received message with key {msg.key()} and value {msg.value().decode('utf-8')}")
                    notification_dict = json.loads(msg.value().decode('utf-8'))
                    notification = self.add_or_update_notification(notification_dict)
                    client_id = str(notification.correlationID)
                    log.info(f"client_id: {client_id}")
                    log.info(f"manager.active_connections: {manager.active_connections}")
                    if manager.active_connections[client_id] is not None:
                        log.info(f"client_id {client_id} is in manager.active_connections - active connection {manager.active_connections[client_id]}")
                        log.info(f"Sending message to client {client_id}")
                        await manager.send_message(client_id, notification.toJSON())

        self.thread = threading.Thread(target=asyncio.run, args=(_consume(),))
        self.thread.start()