# Dockerfile

FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml /app/

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create a virtualenv
RUN poetry config virtualenvs.create true

# Install dependencies
RUN poetry install 
# Copy the rest of the application code
COPY src /app/src
COPY src/api /app/api

copy ../application_default_credentials.json /app/application_default_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/application_default_credentials.json"
ENV GOOGLE_CLOUD_PROJECT="shredit"


CMD ["poetry","run","uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
