import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from starlette.exceptions import HTTPException as StarletteHTTPException

from pizza_library.functions import create_random_order
from pizza_library.messaging import send_pizza_order
from pizza_library.storage import upload_pizza_order
from pizza_shop import SERVICE_NAME

app = FastAPI()

# Configure CORS
origins = ["*"]  # Update this with the allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc):
    context_keys = list(get_current_context().keys())
    if context_keys:
        span_key = context_keys[0]
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
    else:
        return JSONResponse(
            {
                "message": str(exc.detail),
                "trace_id": None,
                "span_id": None
            },
            status_code=exc.status_code
        )


meter = metrics.get_meter_provider().get_meter(__name__)
pizza_counter = meter.create_counter("pizza_order_counter", "number of pizzas ordered", "pizzas")
tracer = trace.get_tracer(__name__)

@app.get("/")
def root():
    with tracer.start_as_current_span("shop"):
        logger = logging.getLogger(SERVICE_NAME)
        logger.setLevel(logging.INFO)
        order = create_random_order()
        pizza_counter.add(len(order.pizzas))
        logger.info(f"Created order: {order}")
        send_pizza_order(order)
        upload_pizza_order(order)
        logger.info(f"Sent order: {order}")
        return {
            "order": order
        }
