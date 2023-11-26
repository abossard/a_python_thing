from enum import Enum
from typing import List
from pydantic import BaseModel


class SizeEnum(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class TypeEnum(str, Enum):
    MEAT = "Meat"
    FISH = "Fish"
    SWEET = "Sweet"
    SPICE = "Spice"
    CHEESE = "Cheese"


class Ingredient(BaseModel):
    unit_of_measure: str
    name: str
    type: TypeEnum
    price_per_unit: float


class Pizza(BaseModel):
    size: SizeEnum
    price: float
    description: str
    ingredients: List[Ingredient]


class Order(BaseModel):
    recipient_name: str
    pizzas: List[Pizza]
    position: int

