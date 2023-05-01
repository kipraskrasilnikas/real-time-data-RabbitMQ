import pika
import random
import os
import signal
import time
import asyncio
from dotenv import load_dotenv
from mappers import get_value_with_suffix

load_dotenv()

# Environment variables
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE")
RABBITMQ_ROUTING_KEY_PREFIX = os.environ.get("RABBITMQ_ROUTING_KEY_PREFIX")
RABBITMQ_QUEUE_PREFIX = os.environ.get("RABBITMQ_QUEUE_PREFIX")
RABBITMQ_QUEUE_COUNT = int(os.environ.get("RABBITMQ_QUEUE_COUNT"))
SAMPLING_RATE = int(os.environ.get("SAMPLING_RATE"))

# RabbitMQ connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
publishProperties = pika.BasicProperties(delivery_mode=2, expiration=str(1000))

channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="direct")

# Variables
queues = []
routingKeys = []


# Delete queues
def delete_queues(signum, frame):
    print("Deleting all queues...")

    for queue in queues:
        channel.queue_delete(queue=queue)

    channel.exchange_delete(exchange=RABBITMQ_EXCHANGE)

    connection.close()


# RabbitMQ queue initialization
def initialize_queues():
    for i in range(RABBITMQ_QUEUE_COUNT):
        queueName = get_value_with_suffix(name=RABBITMQ_QUEUE_PREFIX, index=i)
        routingKey = get_value_with_suffix(name=RABBITMQ_ROUTING_KEY_PREFIX, index=i)

        queues.append(queueName)
        routingKeys.append(routingKey)

        channel.queue_declare(queue=queueName)
        channel.queue_bind(
            queue=queueName, exchange=RABBITMQ_EXCHANGE, routing_key=routingKey
        )


async def publish_data(routingKey):
    data = []

    for i in range(SAMPLING_RATE):
        random_number = str(random.randint(-100, 100))
        data.append(random_number)

    channel.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key=routingKey,
        body=" ".join(data),
        properties=publishProperties,
    )


# Publish messages to RabbitMQ queues
async def publish_data_to_queues():
    while True:
        messageCount = SAMPLING_RATE * RABBITMQ_QUEUE_COUNT

        print(f"Sending {messageCount} data points...")

        await asyncio.gather(*map(publish_data, routingKeys))

        time.sleep(1)


def main():
    signal.signal(signal.SIGINT, delete_queues)
    initialize_queues()
    asyncio.run(publish_data_to_queues())


main()
