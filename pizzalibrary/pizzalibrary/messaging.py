import json
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from opentelemetry import trace

from pizzalibrary.models import Order

PIZZA_ORDER_QUEUE_NAME = os.environ.get('PIZZA_ORDER_QUEUE_NAME')
if PIZZA_ORDER_QUEUE_NAME is None:
    raise ValueError('PIZZA_ORDER_QUEUE_NAME environment variable is not set')

PIZZA_ORDER_CONNECTION_STRING = os.environ.get('PIZZA_ORDER_CONNECTION_STRING')
if PIZZA_ORDER_CONNECTION_STRING is None:
    raise ValueError('PIZZA_ORDER_CONNECTION_STRING environment variable is not set')
tracer = trace.get_tracer(__name__)

def send_pizza_data(data: str):
    with tracer.start_as_current_span(name="send_pizza_data"):
        service_bus_client = ServiceBusClient.from_connection_string(conn_str=PIZZA_ORDER_CONNECTION_STRING,
                                                                     logging_enable=True)

        with service_bus_client.get_queue_sender(queue_name=PIZZA_ORDER_QUEUE_NAME) as sender:
            service_bus_message = ServiceBusMessage(data)
            sender.send_messages(service_bus_message)


def send_pizza_order(order: Order):
    with tracer.start_as_current_span(name="send_pizza_order"):
        envelope = dict(type='order', data=order.model_dump())
        return send_pizza_data(json.dumps(envelope))
