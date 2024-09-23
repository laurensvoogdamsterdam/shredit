# Start with a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Install Poetry and dependencies
RUN pip install poetry 
RUN poetry config virtualenvs.create false 
RUN  poetry install --no-interaction --no-ansi

# Copy the rest of the app
COPY . /app/

# Expose the port for FastAPI
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["poetry", "run", "api", "up"]
