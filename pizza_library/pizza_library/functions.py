import random

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
