from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from starlette.exceptions import HTTPException as StarletteHTTPException
from pizzalibrary.functions import create_random_order
from opentelemetry import metrics
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

PIZZA_ORDER_QUEUE_NAME = os.environ.get('PIZZA_ORDER_QUEUE_NAME')
if PIZZA_ORDER_QUEUE_NAME is None:
    raise ValueError('PIZZA_ORDER_QUEUE_NAME environment variable is not set')

PIZZA_ORDER_CONNECTION_STRING = os.environ.get('PIZZA_ORDER_CONNECTION_STRING')
if PIZZA_ORDER_CONNECTION_STRING is None:
    raise ValueError('PIZZA_ORDER_CONNECTION_STRING environment variable is not set')

service_bus_client = ServiceBusClient.from_connection_string(conn_str=PIZZA_ORDER_CONNECTION_STRING, logging_enable=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application")
    yield
    print("Stopping application")
    

app = FastAPI(lifespan=lifespan)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    span_key = list(get_current_context().keys())[0]
    span = get_current_context().get(span_key)
    assert isinstance(span, _Span)
    return JSONResponse(
        {
            "message": str(exc.detail),
            "trace_id": span.context.trace_id,
            "span_id": span.context.span_id
        },
        status_code=exc.status_code
    )


logger = logging.getLogger(__name__)
meter = metrics.get_meter_provider().get_meter(__name__)
pizza_counter = meter.create_counter("pizza_counter", "number of pizzas ordered", "pizzas")

@app.get("/")
async def root():
    pizza_counter.add(1)
    order = create_random_order()
    logger.info(f"Created order: {order}")
    with service_bus_client.get_queue_sender(queue_name=PIZZA_ORDER_QUEUE_NAME) as sender:
        service_bus_message = ServiceBusMessage(str(order))
        response = sender.send_messages(service_bus_message)
        return {
            "response": response,
            "order": order
        }
