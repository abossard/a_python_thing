import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import metrics
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from pizzalibrary.functions import create_random_order
from pizzalibrary.messaging import send_pizza_data, send_pizza_order
from pizzalibrary.storage import upload_pizza_data, upload_pizza_order
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application")
    yield
    print("Stopping application")


app = FastAPI(lifespan=lifespan)

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
async def http_exception_handler(request: Request, exc):
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

logger = logging.getLogger(__name__)
meter = metrics.get_meter_provider().get_meter(__name__)
pizza_counter = meter.create_counter("pizza_counter", "number of pizzas ordered", "pizzas")


@app.get("/")
async def root():
    order = create_random_order()
    pizza_counter.add(len(order.pizzas))
    logger.info(f"Created order: {order}")
    send_pizza_order(order)
    upload_pizza_order(order)

    return {
        "order": order
    }