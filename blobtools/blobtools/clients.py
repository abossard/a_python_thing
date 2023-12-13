from azure.storage.blob.aio import BlobServiceClient
from azure.storage.queue.aio import QueueClient
from azure.storage.queue import QueueMessage, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy

def get_blob_service_client(storage_connection_string):
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=storage_connection_string
    )
    return blob_service_client

def get_storage_queue_client(storage_connection_string, queue_name) -> QueueClient:
    queue_client = QueueClient.from_connection_string(
        conn_str=storage_connection_string,
        queue_name=queue_name
    )
    queue_client.message_encode_policy = BinaryBase64EncodePolicy()
    queue_client.message_decode_policy = BinaryBase64DecodePolicy()
    return queue_client
