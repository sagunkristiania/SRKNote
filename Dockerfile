FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"


COPY pyproject.toml poetry.lock requirements.txt ./

RUN poetry install --no-root --only main


RUN pip install --upgrade pip \
    && pip install -r requirements.txt


COPY . /app



# Expose port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["poetry", "run", "uvicorn", "src.srknote.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


