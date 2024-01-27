import logging

from opentelemetry import metrics
from opentelemetry import trace

from pizzalibrary.startup import setup_telemetry

setup_telemetry("pizza-maker", "1")

logging.info("Starting application")
from azure.servicebus import ServiceBusClient

logger = logging.getLogger(__name__)
meter = metrics.get_meter_provider().get_meter(__name__)
pizza_counter = meter.create_counter("pizza_made_counter", "number of pizzas made", "pizzas")
tracer = trace.get_tracer(__name__)


with tracer.start_as_current_span(name="RECEIVER"):
    with ServiceBusClient.from_connection_string(connstr) as client:
        # with client.get_queue_sender(queue_name) as sender:
        #     # Sending a single message
        #     single_message = ServiceBusMessage("Single message")
        #     sender.send_messages(single_message)
        # continually receives new messages until it doesn't receive any new messages for 5 (max_wait_time) seconds.
        with client.get_queue_receiver(queue_name=queue_name, max_wait_time=5) as receiver:
            # Receive all messages
            for msg in receiver:
                print("Received: " + str(msg))
                receiver.complete_message(msg)
