import datetime
import uuid
from blobtools.logging import configure_opentelemetry
from dotenv import load_dotenv, find_dotenv
import asyncio
from azure.storage.blob.aio import BlobServiceClient
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
    ordered_on: int = Field(default_factory=lambda: datetime.datetime.now())

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    amount_cent: int
    paid_on: int = Field(default_factory=lambda: datetime.datetime.now())

def create_random_order_payment_pair() -> Tuple[Order, Payment]:
    order = Order(order=secrets.token_hex(64))
    payment = Payment(id=order.id, order_id=order.id, amount_cent=random.randint(1, 10000))
    return order, payment

# Constants from environment variables

SERVICE_NAME = "blobtools:step_1_generate"


configure_opentelemetry(SERVICE_NAME)

def get_blob_service_client():
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=STORAGE_ACCOUNT_CONNECTION_STRING
    )
    return blob_service_client

async def main():
    with trace.get_tracer(__name__).start_as_current_span(SERVICE_NAME):
        blob_service_client = get_blob_service_client()
        # get container client
        container_client = blob_service_client.get_container_client(SAGA_CONTAINER_NAME)
        # create container if not exists
        
        order_payment_pairs = [create_random_order_payment_pair() for _ in range(10)]
        orders, payments = zip(*order_payment_pairs)
        order_payment_list = list(orders) + list(payments)
        random.shuffle(order_payment_list)
        # print id and type of each item in the lit
        for item in order_payment_list:
            print(item.id, item.__class__.__name__)

if __name__ == "__main__":
    asyncio.run(main())
