# -----------------------------
# Base image
# -----------------------------
FROM python:3.10-slim                   # Use a lightweight Python 3.10 image for faster builds

# -----------------------------
# Environment variables
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE 1           # Prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED 1                  # Ensure logs are output immediately without buffering

# -----------------------------
# Set working directory
# -----------------------------
WORKDIR /app                             # All subsequent commands run in /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential                      # Required for compiling Python packages
    curl                                  # Needed to download Poetry installer
    && rm -rf /var/lib/apt/lists/*        # Clean up apt cache to reduce image size

# -----------------------------
# Install Poetry (Python dependency manager)
# -----------------------------
RUN curl -sSL https://install.python-poetry.org | python3 -    # Install Poetry
ENV PATH="/root/.local/bin:$PATH"                              # Add Poetry to PATH

# -----------------------------
# Copy dependency files
# -----------------------------
COPY pyproject.toml poetry.lock requirements.txt ./            # Copy dependency definitions

# -----------------------------
# Install Python dependencies
# -----------------------------
RUN poetry install --no-root --only main                      # Install main dependencies from pyproject.toml
RUN pip install --upgrade pip && pip install -r requirements.txt  # Ensure pip packages from requirements.txt are installed

# -----------------------------
# Copy project code

COPY . /app                                                   # Copy all project files into container

# -----------------------------
# Expose port
# -----------------------------
EXPOSE 8000                                                   # Expose FastAPI default port

# -----------------------------
# Command to run the application
# -----------------------------
CMD ["poetry", "run", "uvicorn", "src.srknote.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Start FastAPI server with Uvicorn, reload enabled for development
