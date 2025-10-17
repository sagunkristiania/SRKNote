# -----------------------------
# Base image
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# Environment variables
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -----------------------------
# Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Poetry
# -----------------------------
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# -----------------------------
# Copy dependency files
# -----------------------------
COPY pyproject.toml poetry.lock requirements.txt ./

# -----------------------------
# Install dependencies
# -----------------------------
RUN poetry install --no-root --only main && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# -----------------------------
# Copy project source code
# -----------------------------
COPY . .

# -----------------------------
# Expose app port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Run FastAPI app
# -----------------------------
CMD ["poetry", "run", "uvicorn", "src.srknote.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
