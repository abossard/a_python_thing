
# Load environment variables
import asyncio
import base64
import json
from blobtools.clients import get_blob_service_client, get_storage_queue_client
from blobtools.logging import configure_opentelemetry
from blobtools.models import Saga, SagaResult, SagaStatus
from dotenv import find_dotenv, load_dotenv
from opentelemetry import trace

load_dotenv(find_dotenv())
from blobtools.config import COMPLETED_SAGA_QUEUE_NAME, NEW_SAGA_QUEUE_NAME, SAGA_CONTAINER_NAME, STORAGE_ACCOUNT_CONNECTION_STRING
import time

SERVICE_NAME = "blobtools:step_2_sagas"
BATCH_SIZE = 32
SLEEP_BETWEEN_LOOPS = 8

configure_opentelemetry(SERVICE_NAME)

async def main():
    message_metric = 0
    completed_saga_metric = 0
    loop_metric = 0
    queue_client = get_storage_queue_client(STORAGE_ACCOUNT_CONNECTION_STRING, NEW_SAGA_QUEUE_NAME)
    result_queue_client = get_storage_queue_client(STORAGE_ACCOUNT_CONNECTION_STRING, COMPLETED_SAGA_QUEUE_NAME)
    blob_service_client = get_blob_service_client(STORAGE_ACCOUNT_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(SAGA_CONTAINER_NAME)

    try:
        while True:
            with trace.get_tracer(__name__).start_as_current_span(f"message-loop-{loop_metric}") as parent_span:
                async for message in queue_client.receive_messages(max_messages=BATCH_SIZE):
                    plain_message = base64.b64decode(message.content).decode("utf-8")
                    parent_span.add_event(f"Received message: {plain_message}", attributes={"message": plain_message})
                    print(f"Received message: {plain_message}")
                    json_message = json.loads(plain_message)
                    subject = json_message['subject']
                    _, _, _, _, container, _, *blob_parts = subject.split('/')
                    blob_name, blob_extension = blob_parts[-1].split('.')
                    blob_type, blob_id = blob_name.split('_')
                    blob_location = '/'.join(blob_parts)
                    blob_path = '/'.join(blob_parts[:-1])
                    print(f"Container: {container}")
                    print(f"Blob Path: {blob_path}")
                    print(f"Blob name: {blob_name}")
                    print(f"Blob location: {blob_location}")
                    print(f"Type: {blob_type}")
                    print(f"ID: {blob_id}")
                    print(f"Extension: {blob_extension}")
                    # get blob lease
                    blob_client = container_client.get_blob_client(blob_location)
                    # has active lease?
                    blob_lease = await blob_client.acquire_lease(-1)
                    tags = await blob_client.get_blob_tags()
                    # if type not in tags, add type from blob_type
                    if 'type' not in tags:
                        tags['type'] = blob_type
                    # if id not in tags, add id from blob_id
                    if 'id' not in tags:
                        tags['id'] = blob_id
                    saga = Saga(**tags)
                    if saga.status == SagaStatus.completed:
                        print(f"This blob is already complete: {saga}")
                        parent_span.add_event(f"This blob is already complete: {saga}", attributes={"saga": saga.model_dump_json()})
                        # we dont do anything here anymore
                    else:
                        # look for other blob
                        other_type = saga.get_other_type()
                        other_blob_location = f"{blob_path}/{other_type.value}_{blob_id}.{blob_extension}"
                        # does it exist?
                        other_blob_client = container_client.get_blob_client(other_blob_location)
                        other_blob_exists = await other_blob_client.exists()
                        if not other_blob_exists:
                            # if not, update status to failed
                            saga.status = SagaStatus.pending
                            print(f"Other blob {other_blob_location} does not exist")
                            parent_span.add_event(f"Other blob {other_blob_location} does not exist", attributes={"other_blob_location": other_blob_location})
                            # dont do anything here anymore
                        else:
                            # if yes, update status to completed
                            saga.status = SagaStatus.completed
                            print(f"Other blob {other_blob_location} exists")
                            other_blob_parts = other_blob_location.split('/')
                            other_blob_name, _ = other_blob_parts[-1].split('.')
                            other_blob_type, other_blob_id = other_blob_name.split('_')
                            # get lease
                            other_blob_lease = await other_blob_client.acquire_lease(-1)
                            # update tags
                            other_tags = await other_blob_client.get_blob_tags()
                            if 'type' not in other_tags:
                                other_tags['type'] = other_blob_type
                            if 'id' not in other_tags:
                                other_tags['id'] = other_blob_id
                            other_saga = Saga(**other_tags)
                            if other_saga.status == SagaStatus.completed:
                                parent_span.add_event(
                                    f"Other blob {other_blob_location} is already complete", 
                                    attributes={"other_saga": other_saga, "other_blob_location": other_blob_location}
                                    )
                                print(f"This blob is already complete: {other_saga}")
                            else:
                                other_saga.status = SagaStatus.completed
                                # PRODUCE THE RESULT!
                                saga_result = SagaResult(sagas=[saga, other_saga], order_location=blob_location, payment_location=other_blob_location)
                                parent_span.add_event(f"Produced result: {saga_result}", attributes={"saga_result": saga_result.model_dump_json()})
                                print(f"Produced result: {saga_result}")
                                completed_saga_metric += 1
                                await result_queue_client.send_message(saga_result.model_dump_json())
                                await other_blob_client.set_blob_tags(other_saga.model_dump(), lease=other_blob_lease)
                                await other_blob_lease.release()
                                await other_blob_client.close()
                        loop_metric += 1
                    # update tags
                    await blob_client.set_blob_tags(saga.model_dump(), lease=blob_lease)
                    await blob_lease.release()
                    await blob_client.close()
                    await queue_client.delete_message(message)
                    parent_span.add_event(f"Deleted message: {message.id}")
                    print(f"Deleted message: {message.id}")
                    parent_span.set_status(trace.Status(trace.StatusCode.OK))
                    message_metric += 1
                parent_span.set_attribute("message_metric", message_metric)
                parent_span.set_attribute("comepleted_saga_metric", completed_saga_metric)
                print(f"Processed {message_metric} messages")
                print(f"Produced {completed_saga_metric} completed sagas")
            print(f"Sleeping for {SLEEP_BETWEEN_LOOPS} seconds")
            await asyncio.sleep(SLEEP_BETWEEN_LOOPS)
    except KeyboardInterrupt:
        print("Keyboard interrupt")
    except Exception as e:
        print(e)
        raise e
    finally:
        print("Closing clients")
        await queue_client.close()
        await result_queue_client.close()
        await container_client.close()
        await blob_service_client.close()

if __name__ == "__main__":
    asyncio.run(main())
