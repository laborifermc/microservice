# Utiliser une image Python légère
FROM python:3.11-slim

# Empêcher Python de générer des fichiers .pyc et forcer l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installer les dépendances système nécessaires pour PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg2-binary \
    pydantic \
    pyzmq

# Copier le code du service
COPY . .

# Exposer les ports ZMQ :
# 5560 : REP (Réponses à la Gateway pour les commandes)
# 5561 : PUB (Événements OrderCreated / OrderLineCreated pour l'Inventory)
EXPOSE 5560
EXPOSE 5561

# Lancer le serveur ZMQ
CMD ["python", "main.py"]