import os
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
NEW_SAGA_QUEUE_NAME = os.getenv("NEW_SAGA_QUEUE_NAME")
COMPLETED_SAGA_QUEUE_NAME = os.getenv("COMPLETED_SAGA_QUEUE_NAME")
SAGA_CONTAINER_NAME = os.getenv("SAGA_CONTAINER_NAME")
TIMESERIES_CONTAINER_NAME=os.getenv("TIMESERIES_CONTAINER_NAME")
