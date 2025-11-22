.PHONY: help build up down logs restart clean dev prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start services in production mode
	docker-compose up -d

down: ## Stop services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

restart: ## Restart services
	docker-compose restart

clean: ## Stop services and remove volumes
	docker-compose down -v
	rm -rf .market_data_cache data/

clean-cache: ## Clear only cache (keep logs, outputs, state)
	docker-compose down
	rm -rf .market_data_cache

init-volumes: ## Initialize persistent volume directories
	bash scripts/init_volumes.sh

backup: ## Backup all persistent data
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/ .market_data_cache/ 2>/dev/null || echo "No data to backup"

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

dev-build: ## Build development images
	docker-compose -f docker-compose.dev.yml build

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

prod: build up ## Build and start production environment

rebuild: clean build up ## Clean, rebuild, and start services

backend-logs: ## View backend logs only
	docker-compose logs -f backend

frontend-logs: ## View frontend logs only
	docker-compose logs -f frontend

shell-backend: ## Access backend container shell
	docker-compose exec backend /bin/bash

shell-frontend: ## Access frontend container shell
	docker-compose exec frontend /bin/sh

