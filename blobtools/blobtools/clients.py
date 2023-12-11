from azure.storage.blob.aio import BlobServiceClient

def get_blob_service_client(storage_connection_string):
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=storage_connection_string
    )
    return blob_service_client
