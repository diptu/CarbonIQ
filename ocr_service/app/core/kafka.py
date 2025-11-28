from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from ocr_service.app.core.config import settings

producer: AIOKafkaProducer | None = None
consumer: AIOKafkaConsumer | None = None


async def init_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
    return producer


async def close_producer():
    global producer
    if producer:
        await producer.stop()
        producer = None


async def create_consumer(topic: str, group_id: str = None):
    global consumer
    # create dedicated consumer instance per call
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id or settings.KAFKA_GROUP_ID,
        enable_auto_commit=True,
    )
    await consumer.start()
    return consumer


async def close_consumer(consumer_instance):
    if consumer_instance:
        await consumer_instance.stop()
