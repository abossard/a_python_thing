from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from starlette.exceptions import HTTPException as StarletteHTTPException



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


@app.get("/")
async def root():
    order = create_random_order()
    return {"message": "Hello World"}
