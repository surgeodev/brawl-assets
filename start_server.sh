#!/bin/bash
# Start the Brawl Assets Hub server with API
PORT=${1:-8080}
cd "$(dirname "$0")"

echo "Starting Brawl Assets Hub on http://localhost:$PORT"
echo "API endpoints:"
echo "  POST /api/add-example     — Add YouTube thumbnail example"  
echo "  POST /api/trigger-scrape  — Trigger GitHub Actions scrape"
echo ""

exec python3 server.py
