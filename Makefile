# Variables
COMPOSE=docker-compose

.PHONY: build up down clean logs test rebuild

# Construit les images Docker de tous les services
build:
	$(COMPOSE) build

# Lance tous les containers en arrière-plan
up:
	$(COMPOSE) up -d

# Arrête les containers sans supprimer les volumes
down:
	$(COMPOSE) down

# Nettoyage complet : arrête les containers, supprime les volumes (base de données)
# et les images orphelines. Très utile pour repartir de zéro.
clean:
	$(COMPOSE) down -v --remove-orphans
	@echo "Nettoyage des volumes et containers terminé."

# Reconstruit tout et relance (la commande préférée des dév)
rebuild:
	$(COMPOSE) up -d --build

# Affiche les logs de tous les services en temps réel
logs:
	$(COMPOSE) logs -f

# Affiche les logs d'un service spécifique (ex: make logs-product)
logs-product:
	$(COMPOSE) logs -f product-service

logs-gateway:
	$(COMPOSE) logs -f gateway-service

# Lance les tests unitaires via le module pytest
test:
	python -m pytest test/test_all_services.py -v