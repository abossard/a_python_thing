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

  type RestaurantVote = {
    restaurant_name: string;
    votes: number;
  };

  const [selectedIngredient, setSelectedIngredient] = useState('');
  const [pizzaOrder, setPizzaOrder] = useState<PizzaOrder | null>(null);
  const [restaurantVotes, setRestaurantVotes] = useState<{ [key: string]: number }>({});
  const [newVote, setNewVote] = useState<RestaurantVote>({ restaurant_name: '', votes: 0 });

  const handleIngredientChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedIngredient(event.target.value);
  };

  const handleVoteChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setNewVote(prevVote => ({
      ...prevVote,
      [name]: name === 'votes' ? parseInt(value) : value
    }));
  };

  const handleVoteSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/vote_restaurant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newVote)
      });
      const data = await response.json();
      console.log(data);
      fetchVotes();
    } catch (error) {
      console.error('Error submitting vote:', error);
    }
  };

  const fetchVotes = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/get_votes');
      const data = await response.json();
      setRestaurantVotes(data);
    } catch (error) {
      console.error('Error fetching votes:', error);
    }
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
    fetchVotes();
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
        <div>
          <h2>Vote for Restaurants</h2>
          <form onSubmit={handleVoteSubmit}>
            <input
              type="text"
              name="restaurant_name"
              value={newVote.restaurant_name}
              onChange={handleVoteChange}
              placeholder="Restaurant Name"
              required
            />
            <input
              type="number"
              name="votes"
              value={newVote.votes}
              onChange={handleVoteChange}
              placeholder="Votes"
              required
            />
            <button type="submit">Submit Vote</button>
          </form>
          <h3>Current Votes</h3>
          <ul>
            {Object.entries(restaurantVotes).map(([restaurant, votes]) => (
              <li key={restaurant}>{restaurant}: {votes} votes</li>
            ))}
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
