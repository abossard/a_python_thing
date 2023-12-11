
# Load environment variables
import asyncio
import base64
import json
from blobtools.clients import get_blob_service_client
from blobtools.logging import configure_opentelemetry
from dotenv import find_dotenv, load_dotenv
from opentelemetry import trace
from azure.storage.queue.aio import QueueClient
from azure.storage.queue import QueueMessage

load_dotenv(find_dotenv())
from blobtools.config import NEW_SAGA_QUEUE_NAME, SAGA_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING


SERVICE_NAME = "blobtools:step_2_sagas"
BATCH_SIZE = 1

configure_opentelemetry(SERVICE_NAME)

def get_storage_queue_client() -> QueueClient:
    return QueueClient.from_connection_string(
        conn_str=STORAGE_ACCOUNT_CONNECTION_STRING,
        queue_name=NEW_SAGA_QUEUE_NAME
    )

async def main():
    with trace.get_tracer(__name__).start_as_current_span(SERVICE_NAME):
        queue_client = get_storage_queue_client()
        blob_service_client = get_blob_service_client(STORAGE_ACCOUNT_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(SAGA_CONTAINER_NAME)

        async for message in queue_client.receive_messages(max_messages=BATCH_SIZE):
            # decode base64 message
            plain_message = base64.b64decode(message.content).decode("utf-8")
            json_message = json.loads(plain_message)
            print(f"Received message: {json_message}")
            subject = json_message['subject']
            _, _, _, _, container, _, *blob_parts = subject.split('/')
            blob_name, blob_extension = blob_parts[-1].split('.')
            blob_type, blob_id = blob_name.split('_')
            blob_path = '/'.join(blob_parts)
            print(f"Container: {container}")
            print(f"Blob Path: {blob_path}")
            print(f"Blob name: {blob_name}")
            print(f"Type: {blob_type}")
            print(f"ID: {blob_id}")
            print(f"Extension: {blob_extension}")
            # get blob lease
            blob_client = container_client.get_blob_client(blob_path)
            blob_lease = await blob_client.acquire_lease(60)
            # relesae blob lease
            await blob_lease.release()
            await queue_client.delete_message(message)

        await queue_client.close()
        await container_client.close()
        await blob_service_client.close()

if __name__ == "__main__":
    asyncio.run(main())
