from aiokafka import AIOKafkaConsumer
import asyncio

import os
bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
print("bootstrap_servers: ", bootstrap_servers)

async def consume():
    try:
        print("Starting consumer")
        
        await asyncio.sleep(120)
        consumer = AIOKafkaConsumer(
            'test',
            bootstrap_servers=bootstrap_servers,
            group_id="my-group",
            auto_offset_reset='earliest')
        # Get cluster layout and join group `my-group`
        await consumer.start()
        print("Consumer started")

        # Consume messages
        await asyncio.sleep(5)
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                    msg.key, msg.value, msg.timestamp)
    except Exception as e:
        print("Exception: ", e)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(consume())