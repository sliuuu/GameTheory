# Docker Setup Guide

This guide explains how to run the Geopolitical Market Game Tracker using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### Production Build

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### Development Build

For development with hot reload:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

Development URLs:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001

## Docker Compose Files

### `docker-compose.yml` (Production)
- Optimized production builds
- Frontend served via nginx
- Backend runs with uvicorn
- Persistent cache volume

### `docker-compose.dev.yml` (Development)
- Hot reload enabled for both services
- Source code mounted as volumes
- Development server configurations

## Building Individual Services

### Backend Only

```bash
docker build -f Dockerfile.backend -t game-theory-backend .
docker run -p 8001:8001 game-theory-backend
```

### Frontend Only

```bash
cd frontend
docker build -t game-theory-frontend .
docker run -p 80:80 game-theory-frontend
```

## Environment Variables

Create a `.env` file (optional) to customize settings:

```env
BACKEND_PORT=8001
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
FRONTEND_PORT=80
```

## Volumes

The application uses persistent volumes for all data that requires durability:

### Persistent Volumes

1. **Market Data Cache** (`market_data_cache`)
   - Location: `.market_data_cache/`
   - Stores: Cached yfinance market data (pickle files)
   - Purpose: Speed up repeated data fetches, reduce API calls

2. **Backend Logs** (`backend_logs`)
   - Location: `data/logs/`
   - Stores: Application logs, error logs
   - Purpose: Debugging, monitoring, audit trail

3. **Model Outputs** (`model_outputs`)
   - Location: `data/outputs/`
   - Stores: Generated plots (backtest_accuracy.png, sensitivity_analysis_*.png)
   - Purpose: Persist analysis results, visualizations

4. **Application State** (`app_state`)
   - Location: `data/state/`
   - Stores: Job state, session data, temporary state files
   - Purpose: Maintain state across container restarts

5. **API History** (`api_history`)
   - Location: `data/api_history/`
   - Stores: Request/response logs, API analytics (JSONL format)
   - Purpose: Track API usage, analytics, debugging

6. **Frontend Logs** (`frontend_logs`)
   - Location: `data/logs/frontend/`
   - Stores: Nginx access/error logs
   - Purpose: Web server logging, access analytics

### Initializing Volumes

Before first run, initialize the directories:

```bash
bash scripts/init_volumes.sh
```

Or manually:

```bash
mkdir -p data/{logs/{backend,frontend},outputs,state,api_history}
mkdir -p .market_data_cache
```

### Volume Backup

To backup all persistent data:

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz data/ .market_data_cache/
```

### Development Volumes

- Source code is mounted for hot reload in dev mode
- Data volumes remain persistent across dev/prod

## Health Checks

Both services include health checks:
- **Backend**: Checks `/` endpoint every 30s
- **Frontend**: Checks nginx status every 30s

## Troubleshooting

### Port Already in Use

If ports 80 or 8001 are in use, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Change frontend port
  - "8002:8001"  # Change backend port
```

### Cache Issues

Clear the cache volume:

```bash
docker-compose down -v
rm -rf .market_data_cache
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Rebuild all services
docker-compose build
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Container Shell

```bash
# Backend
docker-compose exec backend /bin/bash

# Frontend
docker-compose exec frontend /bin/sh
```

## Production Deployment

For production deployment:

1. **Update CORS origins** in `api_backend.py` or via environment variable
2. **Use production docker-compose.yml**
3. **Set up reverse proxy** (nginx/traefik) for SSL termination
4. **Configure environment variables** via `.env` file
5. **Set up monitoring** and logging
6. **Use Docker secrets** for sensitive data

## Multi-stage Build

The frontend uses a multi-stage build:
- **Stage 1**: Build React app with Node.js
- **Stage 2**: Serve with nginx (alpine, minimal size)

This results in a smaller final image (~25MB vs ~1GB).

## Network Configuration

Services communicate via Docker network `game-theory-network`:
- Frontend nginx proxies `/api` requests to `backend:8001`
- Services can communicate using service names

## Performance Tips

1. **Use production build** for better performance
2. **Enable gzip** in nginx (already configured)
3. **Cache static assets** (already configured)
4. **Use volume mounts** for cache persistence
5. **Set resource limits** in production:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

