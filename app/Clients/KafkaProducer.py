import os

from config import is_running_in_docker
from config import logger as log

from confluent_kafka import Producer
from threading import Lock

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
            KAFKA_URL = os.environ.get("KAFKA_URL", 'kafka:9092')
        else:
            KAFKA_URL = os.environ.get("KAFKA_URL", 'localhost:9092')
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