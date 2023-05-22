from confluent_kafka import Consumer, KafkaException
import threading
import os
from config import logger as log
from config import is_running_in_docker

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
                    KAFKA_URL = os.environ.get("KAFKA_URL", "kafka:9092")
                else:
                    KAFKA_URL = os.environ.get("KAFKA_URL", "localhost:9092")
                kafka_config['bootstrap.servers'] = KAFKA_URL
                log.info(f"kafka_config: {kafka_config}")
                self._instance = Consumer(kafka_config)
        except Exception as e:
            log.error(f"KafkaConsumerSingleton.__init__(): {e}")

    def start_consuming(self, topic):
        log.info(f"KafkaConsumerSingleton.start_consuming({topic})")
        self._instance.subscribe([topic])

        def _consume():
            while True:
                msg = self._instance.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    log.error(f"Consumer error: {msg.error()}")
                    raise KafkaException(msg.error())
                else:
                    # Here you can do whatever you want with the messages.
                    log.debug(f"Received message with key {msg.key()} and value {msg.value()}")

        self.thread = threading.Thread(target=_consume)
        self.thread.start()

# kafka_consumer = KafkaConsumerSingleton.getInstance()
# kafka_consumer.start_consuming('test')