# Build stage
FROM python:3.11-slim as builder

# Install poetry
RUN pip install poetry poetry-plugin-export

WORKDIR /app

# editable installs will require the source code
COPY . .

WORKDIR /app/pizza_shop
RUN poetry install

EXPOSE 8000
# Run the project
CMD ["poetry", "run", "python", "-m", "pizza_shop"]