import logging
import os
import time
import random

from opentelemetry import metrics
from opentelemetry import trace

from pizzalibrary.startup import setup_telemetry
SERVICE_NAME = 'pizza_maker'
setup_telemetry(SERVICE_NAME, "1")

logging.info("Starting application")
from azure.servicebus import ServiceBusClient

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
meter = metrics.get_meter_provider().get_meter(SERVICE_NAME)
pizza_counter = meter.create_counter("pizza_made_counter", "number of pizzas made", "pizzas")
tracer = trace.get_tracer(SERVICE_NAME)
pizza_order_queue_name = os.getenv('PIZZA_ORDER_QUEUE_NAME')
pizza_order_connection_string = os.getenv('PIZZA_ORDER_CONNECTION_STRING')


with tracer.start_as_current_span("shift_start"):
    with ServiceBusClient.from_connection_string(pizza_order_connection_string) as client:
        with client.get_queue_receiver(queue_name=pizza_order_queue_name, max_wait_time=5) as receiver:
            # Receive all messages
            for msg in receiver:
                logger.info('starting to make a pizza %s', msg)
                pizza_counter.add(1)
                logger.info('finished making pizza %s', msg)
                receiver.complete_message(msg)
    logger.info('shift end')
    print('time to go home')
