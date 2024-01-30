import asyncio
import random
import time
from multiprocessing import Pool

from opentelemetry import trace

from pizza_library.models import Order, SizeEnum, TypeEnum, Ingredient, Pizza


def create_random_order() -> Order:
    sizes = list(SizeEnum)
    types = list(TypeEnum)
    ingredients = [Ingredient(
        unit_of_measure=random.choice(['grams', 'pieces']),
        name=f'Ingredient {i}',
        type=random.choice(types),
        price_per_unit=random.uniform(0.5, 3.0)
    ) for i in range(random.randint(1, 5))]

    pizzas = [Pizza(
        size=random.choice(sizes),
        price=random.uniform(5.0, 20.0),
        description=f'Pizza {i}',
        ingredients=random.sample(ingredients, random.randint(1, len(ingredients)))
    ) for i in range(random.randint(1, 4))]

    order = Order(
        recipient_name='John Doe',
        pizzas=pizzas,
        position=random.randint(1, 100)
    )

    return order


tracer = trace.get_tracer(__name__)


async def make_the_pizza(pizza_id: int):
    with tracer.start_as_current_span("make_pizza", attributes={"pizza_id": pizza_id}):
        await preheat_oven(200)
        flatten_dough()
        prepare_pizza()
        await bake_pizza()


def make_the_pizza_sync(pizza_id: int):
    with tracer.start_as_current_span("make_pizza_sync", attributes={"pizza_id": pizza_id}):
        preheat_oven_sync(200)
        flatten_dough()
        prepare_pizza()
        bake_pizza_sync()


def preheat_oven_sync(degrees: int):
    with tracer.start_as_current_span("preheat_oven_sync"):
        time.sleep(degrees / 100)


async def preheat_oven(degrees: int):
    with tracer.start_as_current_span("preheat_oven"):
        await asyncio.sleep(degrees / 100)


def prepare_pizza():
    with tracer.start_as_current_span("prepare_pizza"):
        _manual_labor_fibonacci(35)


def flatten_dough():
    with tracer.start_as_current_span("flatten_dough"):
        _manual_labor_fibonacci(34)


async def bake_pizza():
    with tracer.start_as_current_span("bake_pizza"):
        await asyncio.sleep(2)


def bake_pizza_sync():
    with tracer.start_as_current_span("bake_pizza_sync"):
        time.sleep(2)


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def _manual_labor_fibonacci(n):
    return [fib(n)] * 10

#
# def _fibonacci_multiprocessing(n):
#     with Pool(10) as p:
#         return p.map(fib, [n] * 10)
