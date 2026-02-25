# Utiliser une image Python légère
FROM python:3.11-slim

# Éviter la génération de fichiers .pyc et forcer l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail dans le container
WORKDIR /app

# Installer les dépendances système nécessaires pour psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
# On les installe directement ici pour faire simple
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pika \
    sqlalchemy \
    psycopg2-binary \
    pydantic

# Copier tout le contenu du dossier Product-service dans /app
COPY . .

# Exposer le port de FastAPI
EXPOSE 8000

# Commande pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]