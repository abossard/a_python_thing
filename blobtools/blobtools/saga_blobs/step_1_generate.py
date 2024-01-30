import datetime
import logging
import os
import uuid

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

from blobtools.clients import get_blob_service_client
from opentelemetry import metrics
from dotenv import load_dotenv, find_dotenv
import asyncio
from opentelemetry import trace
from pydantic import BaseModel, Field
import secrets
import random
from typing import Tuple

# Load environment variables
load_dotenv(find_dotenv())
from blobtools.config import SAGA_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order: str
    ordered_on: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp()))

    def get_filename(self) -> str:
        timestamp = datetime.datetime.fromtimestamp(self.ordered_on).strftime("%Y/%m/%d")
        return f"{timestamp}/order_{self.ordered_on}_{self.id}.json"


class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    secret_code: str = Field(default_factory=lambda: secrets.token_hex(64))
    amount_cent: int
    paid_on: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp()))

    def get_filename(self) -> str:
        timestamp = datetime.datetime.fromtimestamp(self.paid_on).strftime("%Y/%m/%d")
        return f"{timestamp}/payment_{self.paid_on}_{self.order_id}.json"


def create_random_order_payment_pair() -> Tuple[Order, Payment]:
    order = Order(order=secrets.token_hex(64))
    payment = Payment(id=order.id, order_id=order.id, amount_cent=random.randint(1, 10000), paid_on=order.ordered_on)
    return order, payment


# Constants from environment variables

SERVICE_NAME = "step_1_generate"
BATCH_SIZE = 20
ITEMS_IN_TOTAL = 100
SECONDS_TO_WAIT_BETWEEN_BATCHES = 1

# os.environ.setdefault('OTEL_SERVICE_NAME', SERVICE_NAME)
# configure_azure_monitor(logger_name=SERVICE_NAME)
# DEBUG output
# resource = Resource.create({
#     SERVICE_NAME: SERVICE_NAME,
# })
# tracer_provider = TracerProvider(resource=resource)
# logger_provider = LoggerProvider(resource=resource)
# span_exporter = ConsoleSpanExporter()
# span_processor = BatchSpanProcessor(span_exporter)
# tracer_provider.add_span_processor(span_processor)
# trace.set_tracer_provider(tracer_provider)
#
# metrics_exporter = ConsoleMetricExporter()
# reader = PeriodicExportingMetricReader(metrics_exporter, export_interval_millis=60000)
# metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

logger = logging.getLogger(SERVICE_NAME)
# tracer = trace.get_tracer(__name__)

# meter = metrics.get_meter_provider().get_meter('blobs')
# order_counter = meter.create_counter("order_counter", "number of orders", "orders")
# payment_counter = meter.create_counter("payment_counter", "number of payments", "payments")

# insert somewhere: with tracer.start_as_current_span(f"message-loop-{loop_metric}") as parent_span:

async def main():
    # with tracer.start_as_current_span("Span for correlated logs") as parent_span:
    message_metric = 0
    blob_service_client = get_blob_service_client(STORAGE_ACCOUNT_CONNECTION_STRING)
    # get container client
    container_client = blob_service_client.get_container_client(SAGA_CONTAINER_NAME)
    # create container if not exists

    order_payment_pairs = [create_random_order_payment_pair() for _ in range(ITEMS_IN_TOTAL)]
    orders, payments = zip(*order_payment_pairs)
    order_payment_list = list(orders) + list(payments)
    random.shuffle(order_payment_list)

    async def upload_blob(item):
        blob_client = container_client.get_blob_client(item.get_filename())
        await blob_client.upload_blob(item.model_dump_json())
        print(f"Uploaded {item.get_filename()}")
        await blob_client.close()

    for i in range(0, len(order_payment_list), BATCH_SIZE):
        # parent_span.add_event(f"Uploading batch starting at {i}")
        batch = order_payment_list[i:i + BATCH_SIZE]
        upload_tasks = [upload_blob(item) for item in batch]
        await asyncio.gather(*upload_tasks)
        message_metric += len(batch)
        # parent_span.add_event(f"Uploaded batch starting at {i}")
        await asyncio.sleep(SECONDS_TO_WAIT_BETWEEN_BATCHES)

    await container_client.close()
    await blob_service_client.close()
    # parent_span.set_attribute("message_metric", message_metric)
    print(f"Uploaded {message_metric} messages")

if __name__ == "__main__":
    asyncio.run(main())
