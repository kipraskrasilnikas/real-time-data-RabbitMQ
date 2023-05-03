import pika
import os
import concurrent.futures
import threading
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
RESULTS_INTERVAL = int(os.environ.get("RESULTS_INTERVAL"))

# Variables
channels = []
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
lock = threading.Lock()
all_received = threading.Event()
messages = {"data-key-{}".format(i): [] for i in range(RABBITMQ_QUEUE_COUNT)}


def callback(ch, method, properties, body):
    with lock:
        channel = method.routing_key

        # Append messages to array if channel is not full
        if len(messages) != RESULTS_INTERVAL:
            messages[channel].append(body)

        # Set the all_received event when all channels have RESULTS_INTERVAL of messages
        if all(
            len(messages[channel]) >= RESULTS_INTERVAL
            for messageArray in messages.values()
        ):
            all_received.set()


def create_channels_for_queues():
    # Create a channel and connection for each queue, store all channels
    for i in range(RABBITMQ_QUEUE_COUNT):
        queueName = get_value_with_suffix(name=RABBITMQ_QUEUE_PREFIX, index=i)

        # RabbitMQ connection and channel
        channel = connection.channel()
        channel.basic_consume(
            queue=queueName, on_message_callback=callback, auto_ack=True
        )
        channel.queue_bind(
            exchange=RABBITMQ_EXCHANGE,
            queue=queueName,
            routing_key=RABBITMQ_ROUTING_KEY_PREFIX + str(i + 1),
        )
        channels.append(channel)


# Define the function to run for each queue listener
def listen_to_queues(channel):
    channel.start_consuming()


def listen_to_queues_with_threadpool():
    # Create a thread pool executor and submit a listener function for each queue
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(listen_to_queues, channel) for channel in channels]

        # Wait for all consumers to receive RESULTS_INTERVAL amount of messages
        all_received.wait()

        for channel in channels:
            channel.stop_consuming()

        connection.close()


def main():
    create_channels_for_queues()
    listen_to_queues_with_threadpool()


main()
