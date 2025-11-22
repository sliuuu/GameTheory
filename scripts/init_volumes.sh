#!/bin/bash
# Initialize persistent volume directories

set -e

echo "Creating persistent volume directories..."

# Create data directory structure
mkdir -p data/logs/backend
mkdir -p data/logs/frontend
mkdir -p data/outputs
mkdir -p data/state
mkdir -p data/api_history
mkdir -p .market_data_cache

# Set appropriate permissions
chmod -R 755 data
chmod -R 755 .market_data_cache

echo "✅ Persistent volume directories created:"
echo "  - data/logs/backend"
echo "  - data/logs/frontend"
echo "  - data/outputs"
echo "  - data/state"
echo "  - data/api_history"
echo "  - .market_data_cache"

