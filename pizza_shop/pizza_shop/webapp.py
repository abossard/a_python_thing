import logging
import random
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.context import get_current as get_current_context
from opentelemetry.sdk.trace import _Span
from starlette.exceptions import HTTPException as StarletteHTTPException

from pizza_library.functions import create_random_order, preheat_oven, prepare_pizza, flatten_dough, bake_pizza, \
    make_the_pizza, make_the_pizza_sync
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

# Data structure to store restaurant votes
class RestaurantVote(BaseModel):
    restaurant_name: str
    votes: int

restaurant_votes: Dict[str, int] = {}

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

# hey -n 10 -c 5 http://127.0.0.1:8000/make_pizza
@app.get("/make_pizza")
async def make_pizza():
    pizza_id = random.randint(1, 1000000)
    await make_the_pizza(pizza_id)
    return {
        "message": f"Your pizza with id {pizza_id} is ready!"
    }

# hey -n 10 -c 5 http://127.0.0.1:8000/make_pizza_sync
@app.get("/make_pizza_sync")
def make_pizza_sync():
    pizza_id = random.randint(1, 1000000)
    make_the_pizza_sync(pizza_id)
    return {
        "message": f"Your pizza with id {pizza_id} is ready!"
    }

# New FastAPI endpoint to handle restaurant voting
@app.post("/vote_restaurant")
def vote_restaurant(vote: RestaurantVote):
    if vote.restaurant_name in restaurant_votes:
        restaurant_votes[vote.restaurant_name] += vote.votes
    else:
        restaurant_votes[vote.restaurant_name] = vote.votes
    return {"message": f"Vote recorded for {vote.restaurant_name}"}

@app.get("/get_votes")
def get_votes():
    return restaurant_votes
