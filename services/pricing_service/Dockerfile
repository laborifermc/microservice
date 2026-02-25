FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg2-binary \
    pydantic \
    pyzmq \
    fastapi \
    uvicorn

COPY . .

# Port ZMQ REP
EXPOSE 5556

# Note: Si ton main.py de Pricing contient un FastAPI pour le /health, 
# utilise uvicorn. Sinon, utilise python main.py.
CMD ["python", "main.py"]