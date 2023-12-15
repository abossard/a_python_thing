import datetime
import uuid
from blobtools.clients import get_blob_service_client
from blobtools.logging import configure_opentelemetry
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
from blobtools.config import TIMESERIES_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING

class GPSData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    starts_on: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp()-60*60))
    ends_on: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp()))
    gps_data: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    def get_filename(self) -> str:
        timestamp = datetime.datetime.fromtimestamp(self.ordered_on).strftime("%Y/%m/%d")
        return f"{timestamp}/{self.device_id}/gps_{self.device_id}_{self.id}.json"
    
    def tags(self) -> dict:
        return {
            "device_id": self.device_id,
            "starts_on": self.starts_on,
            "ends_on": self.ends_on
        }


def create_random_gps_data(timerange) -> GPSData:
    pass

# Constants from environment variables

SERVICE_NAME = f"blobtools:{__name__}"
BATCH_SIZE = 100
ITEMS_IN_TOTAL = 1000
SECONDS_TO_WAIT_BETWEEN_BATCHES = 0.5

configure_opentelemetry(SERVICE_NAME)
meter = metrics.get_meter_provider().get_meter('blobs')
order_counter = meter.create_counter("order_counter", "number of orders", "orders")
payment_counter = meter.create_counter("payment_counter", "number of payments", "payments")

async def main():
    message_metric = 0
    with trace.get_tracer(__name__).start_as_current_span("generating-data") as parent_span:
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
            parent_span.add_event(f"Uploading batch starting at {i}")
            batch = order_payment_list[i:i+BATCH_SIZE]
            upload_tasks = [upload_blob(item) for item in batch]
            await asyncio.gather(*upload_tasks)
            message_metric += len(batch)
            parent_span.add_event(f"Uploaded batch starting at {i}")
            await asyncio.sleep(SECONDS_TO_WAIT_BETWEEN_BATCHES)

        await container_client.close()
        await blob_service_client.close()
        parent_span.set_attribute("message_metric", message_metric)
        print(f"Uploaded {message_metric} messages")
if __name__ == "__main__":
    asyncio.run(main())
