from datetime import datetime
import json
from aiokafka import AIOKafkaProducer
import asyncio

import os
bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
print("bootstrap_servers: ", bootstrap_servers)

async def send_one():
    print("Starting producer")
    await asyncio.sleep(80)
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers)
    # Get cluster layout and initial topic/partition leadership information
    try:
        await producer.start()
        print("Producer started")
    
        # Produce message
        await asyncio.sleep(5)
        message = {
            "message": "Hello World",
            "timestamp": datetime.now().isoformat()
        }

        message_bytes = json.dumps(message).encode('utf-8')
        
        await producer.send_and_wait("test", message_bytes)
        print(f"Message sent: {message}")
    except Exception as e:
        print("Exception: ", e)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
        print("Producer stopped")

asyncio.run(send_one())