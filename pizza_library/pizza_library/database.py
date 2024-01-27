import sqlite3
from pizza_library.models import Ingredient, Order, Pizza
from pydantic import BaseModel, parse_obj_as
from enum import Enum
from typing import List
import os
# Enum and BaseModel definitions as per your schema
def flush_database():
    db_file = 'pizza_orders.db'
    if os.path.exists(db_file):
        os.remove(db_file)
# Database Initialization
def initialize_database():
    conn = sqlite3.connect('pizza_orders.db')
    
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                        id INTEGER PRIMARY KEY,
                        unit_of_measure TEXT,
                        name TEXT,
                        type TEXT,
                        price_per_unit REAL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pizzas (
                        id INTEGER PRIMARY KEY,
                        size TEXT,
                        price REAL,
                        description TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pizza_ingredients (
                        pizza_id INTEGER,
                        ingredient_id INTEGER,
                        FOREIGN KEY(pizza_id) REFERENCES pizzas(id),
                        FOREIGN KEY(ingredient_id) REFERENCES ingredients(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY,
                        recipient_name TEXT,
                        position INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                        order_id INTEGER,
                        pizza_id INTEGER,
                        FOREIGN KEY(order_id) REFERENCES orders(id),
                        FOREIGN KEY(pizza_id) REFERENCES pizzas(id))''')

    conn.commit()
    conn.close()

# Add Data Models here

# Further implementations for CRUD operations and Business Logic

def get_order(cursor, order_id: int) -> Order:
    query = """
        SELECT o.recipient_name, o.position,
               p.id as pizza_id, p.size, p.price, p.description,
               i.unit_of_measure, i.name, i.type, i.price_per_unit
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN pizzas p ON oi.pizza_id = p.id
        LEFT JOIN pizza_ingredients pi ON p.id = pi.pizza_id
        LEFT JOIN ingredients i ON pi.ingredient_id = i.id
        WHERE o.id = ?
    """

    cursor.execute(query, (order_id,))
    rows = cursor.fetchall()

    # Processing the result to build the Order object
    if not rows:
        return None  # or raise an exception

    pizzas = {}
    for row in rows:
        pizza_id = row['pizza_id']
        if pizza_id not in pizzas:
            pizzas[pizza_id] = {
                "size": row['size'],
                "price": row['price'],
                "description": row['description'],
                "ingredients": []
            }
        if row['name']:  # check if the ingredient exists
            ingredient = Ingredient(
                unit_of_measure=row['unit_of_measure'],
                name=row['name'],
                type=row['type'],
                price_per_unit=row['price_per_unit']
            )
            pizzas[pizza_id]['ingredients'].append(ingredient)

    pizza_objs = [Pizza(**pizza) for pizza in pizzas.values()]
    return Order(recipient_name=rows[0]['recipient_name'], position=rows[0]['position'], pizzas=pizza_objs)


def insert_sample_data():
    connection = sqlite3.connect('pizza_orders.db')
    cursor = connection.cursor()

    # Inserting sample ingredients
    ingredients = [
        ("Gram", "Tomato", "Spice", 0.5),
        ("Piece", "Cheese", "Cheese", 0.75),
        ("Gram", "Pepperoni", "Meat", 1.0),
    ]
    cursor.executemany("INSERT INTO ingredients (unit_of_measure, name, type, price_per_unit) VALUES (?, ?, ?, ?)", ingredients)

    # Inserting sample pizza
    pizza = ("Medium", 15.0, "Pepperoni Pizza")
    cursor.execute("INSERT INTO pizzas (size, price, description) VALUES (?, ?, ?)", pizza)
    pizza_id = cursor.lastrowid

    # Linking pizza with ingredients
    ingredient_ids = cursor.execute("SELECT id FROM ingredients").fetchall()
    pizza_ingredients = [(pizza_id, ingredient_id[0]) for ingredient_id in ingredient_ids]
    cursor.executemany("INSERT INTO pizza_ingredients (pizza_id, ingredient_id) VALUES (?, ?)", pizza_ingredients)

    # Inserting sample order
    order = ("John Doe", 1)
    cursor.execute("INSERT INTO orders (recipient_name, position) VALUES (?, ?)", order)
    order_id = cursor.lastrowid

    # Linking order with pizza
    order_item = (order_id, pizza_id)
    cursor.execute("INSERT INTO order_items (order_id, pizza_id) VALUES (?, ?)", order_item)

    connection.commit()
    cursor.close()
    connection.close()
    return order_id


def main():
    order_id = insert_sample_data()
    print('inserted sample data with order id', order_id)

    connection = sqlite3.connect('pizza_orders.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    order = get_order(cursor, order_id)
    print(order)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    flush_database()
    initialize_database()
    main()
