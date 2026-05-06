#!/bin/bash

# ===== COLORS =====
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== HEADER =====
echo -e "${BLUE}"
echo "======================================"
echo "     DOCKER MANAGEMENT TOOL 🚀"
echo "======================================"
echo -e "${NC}"

# ===== ANIMATION FUNCTION =====
loading() {
    echo -n "$1"
    for i in {1..5}; do
        echo -n "."
        sleep 0.4
    done
    echo ""
}

# ===== STEP 1 =====
echo -e "${YELLOW}Step 1: Stop Docker containers${NC}"

read -p "Do you want to remove volumes too? (yes/no): " vol_choice

loading "Stopping containers"

if [[ "$vol_choice" == "yes" ]]; then
    echo -e "${RED}Stopping containers + removing volumes...${NC}"
    docker compose -f Docker/docker-compose.yml down -v
    echo -e "${RED}✔ Containers + volumes removed${NC}"
else
    echo -e "${YELLOW}Stopping containers only...${NC}"
    docker compose -f Docker/docker-compose.yml down
    echo -e "${GREEN}✔ Containers stopped (volumes kept)${NC}"
fi

echo ""

sleep 2

# ===== STEP 2 =====
read -p "Build Container or Up? (build/up): " build_up

echo ""

if [[ "$build_up" == "build" ]]; then
    echo -e "${YELLOW}Building and starting containers...${NC}"
    loading "Building"
    docker compose -f Docker/docker-compose.yml up -d --build
else
    echo -e "${YELLOW}Starting containers...${NC}"
    loading "Starting"
    docker compose -f Docker/docker-compose.yml up -d
fi

echo -e "${GREEN}✔ Containers are running${NC}"
echo ""

# ===== STEP 3 =====
echo -e "${BLUE}Migration Logs Section${NC}"
read -p "Do you want to see logs of migration? (yes/no): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Showing migration logs...${NC}"
    sleep 1
    docker logs -f medihub_migrate
fi


# ===== STEP 4 =====
echo -e "${BLUE}Seed Section Management ${NC}"
read -p "Do you want to run root seet management commands? (yes/no): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Running root seed...${NC}"
    sleep 1
    docker exec medihub_web1 python manage.py root_seed
fi



echo ""
echo -e "${GREEN}======================================"
echo "May Allah give you Strength, Knowledge,"
echo "Patience and Success. Thanks 🤲"
echo "======================================"
echo -e "${NC}"



