# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
# Install poetry
RUN pip install poetry


# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml pizza_shop/poetry.lock ./

# Install dependencies
RUN poetry export -f requirements.txt --output requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Copy source code

# Build the project as a wheel
RUN poetry build

# Deploy stage
FROM python:3.11-slim as final

# Copy only the wheels we need
COPY --from=builder /wheels /wheels
COPY --from=builder /dist /dist

# Install the project and its dependencies
RUN pip install --no-cache /wheels/*.whl \
    && pip install --no-cache /dist/*.whl

EXPOSE 8000
# Run the project
CMD ["python", "-m", "pizza_shop"]