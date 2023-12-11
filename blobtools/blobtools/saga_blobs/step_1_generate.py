from blobtools.logging import configure_opentelemetry
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from azure.storage.blob.aio import BlobServiceClient
from opentelemetry import trace

# Load environment variables
load_dotenv(find_dotenv())

# Constants from environment variables
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
NEW_SAGA_QUEUE_NAME = os.getenv("NEW_SAGA_QUEUE_NAME")
COMPLETED_SAGA_QUEUE_NAME = os.getenv("COMPLETED_SAGA_QUEUE_NAME")
SAGA_CONTAINER_NAME = os.getenv("SAGA_CONTAINER_NAME")

SERVICE_NAME = "blobtools:step_1_generate"

load_dotenv(find_dotenv()) 

configure_opentelemetry(SERVICE_NAME)


def get_blob_service_client():
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=STORAGE_ACCOUNT_CONNECTION_STRING
    )
    return blob_service_client

async def main():
    with trace.get_tracer(__name__).start_as_current_span(SERVICE_NAME):
        # Your code logic here
        pass

if __name__ == "__main__":
    asyncio.run(main())
