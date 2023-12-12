from azure.storage.blob.aio import BlobServiceClient
from azure.storage.queue.aio import QueueClient
from azure.storage.queue import QueueMessage

def get_blob_service_client(storage_connection_string):
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=storage_connection_string
    )
    return blob_service_client

def get_storage_queue_client(storage_connection_string, queue_name) -> QueueClient:
    return QueueClient.from_connection_string(
        conn_str=storage_connection_string,
        queue_name=queue_name
    )
