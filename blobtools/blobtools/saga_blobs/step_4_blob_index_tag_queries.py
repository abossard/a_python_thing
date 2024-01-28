import asyncio
import datetime

from dotenv import find_dotenv, load_dotenv

from blobtools.clients import get_blob_service_client, get_storage_queue_client

load_dotenv(find_dotenv())
from blobtools.config import SAGA_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING, NEW_SAGA_QUEUE_NAME

SERVICE_NAME = "step_4_blob_index_tag_queries"
TS_15_MINUTES_AGO = int(datetime.datetime.now().timestamp()) - 60 * 15
ORDER_PENDING_TAG_FILTER = f"@container = '{SAGA_CONTAINER_NAME}' AND \"status\"='pending' AND \"type\"='order' AND \"ts\" > '{TS_15_MINUTES_AGO}'"
PAYMENT_PENDING_TAG_FILTER = f"@container = '{SAGA_CONTAINER_NAME}' AND \"status\"='pending' AND \"type\"='payment' AND \"ts\" > '{TS_15_MINUTES_AGO}'"


async def main():
    blob_service_client = get_blob_service_client(STORAGE_ACCOUNT_CONNECTION_STRING)
    storage_queue_client = get_storage_queue_client(STORAGE_ACCOUNT_CONNECTION_STRING, NEW_SAGA_QUEUE_NAME)

    async def get_pending_order_names():
        return [blob.name async for blob in blob_service_client.find_blobs_by_tags(ORDER_PENDING_TAG_FILTER)]

    async def get_pending_payment_names():
        return [blob.name async for blob in blob_service_client.find_blobs_by_tags(PAYMENT_PENDING_TAG_FILTER)]

    pending_order_names, pending_payment_names = await asyncio.gather(
        get_pending_order_names(),
        get_pending_payment_names()
    )

    print(f"Pending orders of the last 15mins: {len(pending_order_names)}")
    print(f"Pending payments of the last 15mins: {len(pending_payment_names)}")
    # subjects = [json.dumps({"subject": f"_/_/_/_/_/_/{name}"}) for name in pending_order_names + pending_payment_names]
    # send_tasks = [storage_queue_client.send_message(subject) for subject in subjects]
    # await asyncio.gather(*send_tasks)
    await blob_service_client.close()
    await storage_queue_client.close()


if __name__ == "__main__":
    asyncio.run(main())
