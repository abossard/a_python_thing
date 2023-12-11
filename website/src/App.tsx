
import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const ingredients = {
    MEAT: "Meat",
    FISH: "Fish",
    SWEET: "Sweet",
    SPICE: "Spice",
    CHEESE: "Cheese"
  };

  type PizzaIngredient = {
    unit_of_measure: string;
    name: string;
    type: string;
    price_per_unit: number;
  };

  type Pizza = {
    size: string;
    price: number;
    description: string;
    ingredients: PizzaIngredient[];
  };

  type PizzaOrder = {
    order: {
      recipient_name: string;
      pizzas: Pizza[];
      position: number;
    };
  };

  const [selectedIngredient, setSelectedIngredient] = useState('');
  const [pizzaOrder, setPizzaOrder] = useState<PizzaOrder | null>(null);

  const handleIngredientChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedIngredient(event.target.value);
  };

  useEffect(() => {
    const fetchPizzaOrder = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000');
        const data = await response.json();
        setPizzaOrder(data);
      } catch (error) {
        console.error('Error fetching pizza order:', error);
      }
    };

    fetchPizzaOrder();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
        <select value={selectedIngredient} onChange={handleIngredientChange}>
          <option value="">Select an ingredient</option>
          {Object.values(ingredients).map((ingredient) => (
            <option key={ingredient} value={ingredient}>{ingredient}</option>
          ))}
        </select>
        <p>You selected: {selectedIngredient}</p>
        {pizzaOrder && (
          <div>
            <p>Recipient: {pizzaOrder.order.recipient_name}</p>
            <table>
              <thead>
                <tr>
                  <th>Pizza Size</th>
                  <th>Price</th>
                  <th>Description</th>
                  <th>Ingredients</th>
                </tr>
              </thead>
              <tbody>
                {pizzaOrder.order.pizzas.map((pizza, index) => (
                  <tr key={index}>
                    <td>{pizza.size}</td>
                    <td>{pizza.price}</td>
                    <td>{pizza.description}</td>
                    <td>
                      <ul>
                        {pizza.ingredients.map((ingredient, index) => (
                          <li key={index}>
                            {ingredient.name} ({ingredient.unit_of_measure}): ${ingredient.price_per_unit}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </header>
    </div>
  );
}

export default App;

