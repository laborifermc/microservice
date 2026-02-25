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
EXPOSE 5557

CMD ["python", "main.py"]