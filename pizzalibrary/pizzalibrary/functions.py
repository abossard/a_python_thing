import random
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

from pizzalibrary.models import Order, SizeEnum, TypeEnum, Ingredient, Pizza

PIZZA_ORDER_QUEUE_NAME = os.environ.get('PIZZA_ORDER_QUEUE_NAME')
if PIZZA_ORDER_QUEUE_NAME is None:
    raise ValueError('PIZZA_ORDER_QUEUE_NAME environment variable is not set')

PIZZA_ORDER_CONNECTION_STRING = os.environ.get('PIZZA_ORDER_CONNECTION_STRING')
if PIZZA_ORDER_CONNECTION_STRING is None:
    raise ValueError('PIZZA_ORDER_CONNECTION_STRING environment variable is not set')

service_bus_client = ServiceBusClient.from_connection_string(conn_str=PIZZA_ORDER_CONNECTION_STRING,
                                                             logging_enable=True)


def send_pizza_order(order: Order):
    with service_bus_client.get_queue_sender(queue_name=PIZZA_ORDER_QUEUE_NAME) as sender:
        service_bus_message = ServiceBusMessage(str(order))
        sender.send_messages(service_bus_message)


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
