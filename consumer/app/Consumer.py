from confluent_kafka import Consumer, KafkaException
import threading
from Models.NotificationModel import NotificationModel
from config import logger as log
import json

from Clients.WebSocketManager import WebSocketManager as WSClient

import asyncio

from config import settings

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
                kafka_config = {}
                kafka_config['bootstrap.servers'] = f"{settings.kafka_server}:{settings.kafka_port}"
                kafka_config['group.id'] = settings.kafka_groupId
                kafka_config['auto.offset.reset'] = 'earliest'
                log.info(f"kafka_config: {kafka_config}")
                self._instance = Consumer(kafka_config)
        except Exception as e:
            log.error(f"KafkaConsumerSingleton.__init__(): {e}")

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
                    notification = NotificationModel(**notification_dict)
                    client_id = str(notification.requestID)
                    log.info(f"client_id: {client_id}")
                    log.info(f"manager.active_connections: {manager.active_connections}")
                    if manager.active_connections[client_id] is not None:
                        log.info(f"client_id {client_id} is in manager.active_connections - active connection {manager.active_connections[client_id]}")
                        log.info(f"Sending message to client {client_id}")
                        await manager.send_message(client_id, notification.toJSON())

        self.thread = threading.Thread(target=asyncio.run, args=(_consume(),))
        self.thread.start()