#!/bin/sh

echo "Creating SSL certificates..."
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/privkey.pem \
  -out nginx/certs/fullchain.pem \
  -subj "/C=BD/ST=Dhaka/L=Dhaka/O=Medihub/CN=localhost"

echo "Starting Docker containers..."
docker compose -f Docker/docker-compose.yml up -d --build

echo "Done! Visit https://localhost"
