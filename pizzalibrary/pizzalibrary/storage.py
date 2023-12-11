# library to store pizza orders and payment informations to azure storage blob

import os
import logging
import json

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.identity import DefaultAzureCredential
from pizzalibrary.models import Order
from datetime import datetime
blob_service_client = None

PIZZA_STORAGE_CONNECTION_STRING = os.environ.get('PIZZA_STORAGE_CONNECTION_STRING')
PIZZA_STORAGE_ACCOUNT_NAME = os.environ.get('PIZZA_STORAGE_ACCOUNT_NAME')
PIZZA_STORAGE_CONTAINER_NAME = os.environ.get('PIZZA_STORAGE_CONTAINER_NAME')
if (not PIZZA_STORAGE_CONNECTION_STRING) and PIZZA_STORAGE_ACCOUNT_NAME:
    blob_service_client = BlobServiceClient(credential=DefaultAzureCredential(), logging_enable=True, account_url=f'https://{PIZZA_STORAGE_ACCOUNT_NAME}.blob.core.windows.net')
elif PIZZA_STORAGE_CONNECTION_STRING: 
    blob_service_client = BlobServiceClient.from_connection_string(PIZZA_STORAGE_CONNECTION_STRING)
else:
    raise ValueError('PIZZA_STORAGE_CONNECTION_STRING or PIZZA_STORAGE_ACCOUNT_NAME environment variable is not set')

blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('PIZZA_STORAGE_CONNECTION_STRING'))

def upload_pizza_order(order: Order):
    # create a filename variable with a path like YYYY/MM/DD/HHMMSS-HASHOORDER.json
    now = datetime.now()
    filename = f'{now.strftime("%Y/%m/%d/")}order-{order.id}.json'
    upload_pizza_data(filename, order.model_dump_json())

def upload_pizza_data(filename: str, content: str):

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=PIZZA_STORAGE_CONTAINER_NAME, blob=filename)
    blob_client.upload_blob(content, overwrite=True)