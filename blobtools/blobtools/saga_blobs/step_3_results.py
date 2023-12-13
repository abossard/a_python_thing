
import asyncio
import json
from blobtools.clients import get_blob_service_client, get_storage_queue_client
from blobtools.logging import configure_opentelemetry
from blobtools.models import SagaResult
from dotenv import find_dotenv, load_dotenv
from opentelemetry import trace

load_dotenv(find_dotenv())
from blobtools.config import COMPLETED_SAGA_QUEUE_NAME, NEW_SAGA_QUEUE_NAME, SAGA_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING


SERVICE_NAME = f"blobtools:{__name__}"
BATCH_SIZE = 100
SLEEP_BETWEEN_LOOPS = 8
configure_opentelemetry(SERVICE_NAME)

async def main():
    message_metric = 0
    last_message_metric = 0
    loop_metric = 0

    try:
        queue_client = get_storage_queue_client(STORAGE_ACCOUNT_CONNECTION_STRING, COMPLETED_SAGA_QUEUE_NAME)
        while True:
            with trace.get_tracer(__name__).start_as_current_span(f"message-loop-{loop_metric}") as parent_span:
                last_message_metric = message_metric
                async for message in queue_client.receive_messages(max_messages=BATCH_SIZE):
                    plain_message = message.content
                    parent_span.add_event(f"Received message: {plain_message}", attributes={"message": plain_message})
                    json_message = json.loads(plain_message)
                    saga_result = SagaResult(**json_message)
                    print(f"Order Location: {saga_result.order_location}, Payment Location: {saga_result.payment_location}")
                    await queue_client.delete_message(message)
                    message_metric += 1
                parent_span.set_attribute("message_metric", message_metric)
                print(f"Processed {message_metric} completed sagas.")

            print(f"Sleeping for {SLEEP_BETWEEN_LOOPS} seconds...")
            if message_metric == last_message_metric:
                await asyncio.sleep(SLEEP_BETWEEN_LOOPS)
            loop_metric += 1
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, exiting...")
    except Exception as e:
        print(f"Exception occurred: {e}")
        raise e
    finally:
        print("Exiting...")
        await queue_client.close()

if __name__ == "__main__":
    asyncio.run(main())
