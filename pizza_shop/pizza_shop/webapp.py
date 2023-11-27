from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from starlette.exceptions import HTTPException as StarletteHTTPException
from pizzalibrary.functions import create_random_order


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


@app.get("/")
async def root():
    order = create_random_order()
    logger.info(f"Created order: {order}")
    logger.debug("Debugging order creation")
    logger.warning("Warning order creation")
    logger.error("Error order creation")
    return {
        "message": "Hello World!",
        "order": order
    }
