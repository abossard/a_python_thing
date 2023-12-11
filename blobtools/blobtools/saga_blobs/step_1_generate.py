from blobtools.logging import configure_opentelemetry
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from azure.storage.blob.aio import BlobServiceClient
from opentelemetry import trace


load_dotenv(find_dotenv()) 

configure_opentelemetry("blobtools:step_1_generate")


def get_blob_service_client():
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    )
    return blob_service_client

async def main():
    with trace.get_tracer(__name__).start_as_current_span("example-span"):
        # Your code logic here
        pass

if __name__ == "__main__":
    asyncio.run(main())
