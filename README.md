# Real-Time data streaming in RabbitMQ

A project that sends 500 numbers (ranging from -100 to 100) generated at random, through the selected amount of channels(queues) in real time.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed the latest version of Python 3
- You have installed RabbitMQ on your system

## Installation

1. Clone the Git repository to your local machine using the command `git clone https://github.com/kipraskrasilnikas/real-time-data-RabbitMQ/`
2. Open a terminal or command prompt and navigate to the directory where you cloned the repository.
3. Install the required dependencies by running pip install -r requirements.txt
4. Create a .env file in the root directory of the project with the following environment variables:
  - RABBITMQ_HOST: The hostname of your RabbitMQ instance
  - RABBITMQ_EXCHANGE: The name of the RabbitMQ exchange to use
  - RABBITMQ_ROUTING_KEY_PREFIX: The prefix for the routing keys used to publish messages to the queues
  - RABBITMQ_QUEUE_PREFIX: The prefix for the names of the RabbitMQ queues to use
  - RABBITMQ_QUEUE_COUNT: The number of RabbitMQ queues to use
  - SAMPLING_RATE: The number of random numbers to generate and publish to each queue every second
  - RESULTS_INTERVAL: The number of messages to receive before stopping the subscriber

## Usage

### Publisher

To start the publisher, run python publisher.py from the root directory of the project. The publisher will generate random numbers and publish them to the specified RabbitMQ queues

### Subscriber

To start the subscriber, run python subscriber.py from the root directory of the project. The subscriber will listen to the RabbitMQ queues and collect the published messages. Once it has received the specified number of messages, it will stop listening to the queues and print the collected messages.

##Notes
- Make sure your RabbitMQ instance is running before starting the publisher and subscriber.
- If you need to change any of the environment variables, update the .env file before starting the publisher and subscriber.
- The mappers.py file contains a helper function used to generate the names of the RabbitMQ queues and routing keys. You don't need to modify this file unless you want to change the naming scheme for the queues and routing keys.
