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

# ===== CHECK REQUIRED FILES =====
if [ ! -f ".env" ]; then
    echo -e "${RED}✘ .env file not found! Aborting.${NC}"
    exit 1
fi
echo -e "${GREEN}✔ .env found${NC}"

echo ""





read -p "Do you want to remove volumes too? (down -v/down/exit/ignore): " vol_choice

loading "Stopping containers"

if [[ "$vol_choice" == "down -v" ]]; then
    echo -e "${RED}Stopping containers + removing volumes...${NC}"
    docker compose -f Docker/docker-compose.yml down -v
    echo -e "${RED}✔ Containers + volumes removed${NC}"
elif [[ "$vol_choice" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$vol_choice" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
else
    echo -e "${YELLOW}Stopping containers only...${NC}"
    docker compose -f Docker/docker-compose.yml down
    echo -e "${GREEN}✔ Containers stopped (volumes kept)${NC}"
fi

echo ""

sleep 2




# ===== STEP 2 =====
read -p "Build Container or Up? (build/up/exit/ignore): " build_up

echo ""

if [[ "$build_up" == "build" ]]; then
    echo -e "${YELLOW}Removing old image...${NC}"
    docker rmi medihub_web 2>/dev/null && echo -e "${GREEN}✔ Old image removed${NC}" || echo -e "${YELLOW}No old image found, skipping...${NC}"
    echo ""
    echo -e "${YELLOW}Building new image...${NC}"
    loading "Building"
    docker compose -f Docker/docker-compose.yml --profile build build web_base
    echo -e "${GREEN}✔ Image built${NC}"
    echo ""
    echo -e "${YELLOW}Starting containers...${NC}"
    loading "Starting"
    docker compose -f Docker/docker-compose.yml up -d
elif [[ "$build_up" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$build_up" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
else
    echo -e "${YELLOW}Starting containers...${NC}"
    loading "Starting"
    docker compose -f Docker/docker-compose.yml up -d
    echo -e "${GREEN}✔ Containers are running${NC}"
fi
echo ""





# ===== WEB1 LOGS =====
echo -e "${BLUE}Web1 Logs Section${NC}"
read -p "Do you want to see web1 logs? (yes/no/exit/ignore): " web1_logs

if [[ "$web1_logs" == "yes" ]]; then
    echo -e "${YELLOW}Showing web1 logs (last 50 lines)...${NC}"
    docker logs --tail=50 medihub_web1
elif [[ "$web1_logs" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$web1_logs" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
fi

echo ""




# ===== STEP 3 =====
echo -e "${BLUE}Migration Logs Section${NC}"
read -p "Do you want to see logs of migration? (yes/no/exit/ignore): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Showing migration logs...${NC}"
    sleep 1
    docker logs -f medihub_migrate
elif [[ "$answer" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$answer" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
fi

echo ""





# ===== STEP 3.5 =====
echo -e "${BLUE}Make Migrations Section${NC}"
read -p "Do you want to run makemigrations? (yes/no/exit/ignore): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Running makemigrations...${NC}"
    loading "Detecting changes"
    if docker compose -f Docker/docker-compose.yml run --rm migrate python manage.py makemigrations; then
        echo -e "${GREEN}✔ Makemigrations completed${NC}"
    else
        echo -e "${RED}✘ Makemigrations failed${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Running migrate...${NC}"
    loading "Applying migrations"
    if docker compose -f Docker/docker-compose.yml run --rm migrate python manage.py migrate; then
        echo -e "${GREEN}✔ Migrate completed${NC}"
    else
        echo -e "${RED}✘ Migrate failed${NC}"
        exit 1
    fi
elif [[ "$answer" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$answer" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
fi

echo ""









# ===== STEP 4 =====
echo -e "${BLUE}Seed Section Management${NC}"
read -p "Do you want to run root seed management commands? (yes/no/exit/ignore): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Running root seed...${NC}"
    sleep 1
    if docker exec medihub_web1 python manage.py root_seed; then
        echo -e "${GREEN}✔ Root seed completed${NC}"
    else
        echo -e "${RED}✘ Root seed failed — is medihub_web1 running?${NC}"
    fi
elif [[ "$answer" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$answer" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
fi

echo ""









# ===== STEP 5 =====
echo -e "${BLUE}Superuser Creation Section${NC}"
read -p "Do you want to create a Django superuser? (yes/no/exit/ignore): " answer

if [[ "$answer" == "yes" ]]; then
    echo -e "${YELLOW}Opening Django superuser creation...${NC}"
    sleep 1
    docker exec -it medihub_web1 python manage.py createsuperuser
    echo -e "${GREEN}✔ Superuser creation process finished${NC}"
elif [[ "$answer" == "exit" ]]; then
    echo -e "${YELLOW}Exit from Shell${NC}"
    exit
elif [[ "$answer" == "ignore" ]]; then
    echo -e "${YELLOW}Ignoring this action${NC}"
fi








echo ""
echo -e "${BLUE}======================================"
echo "       DEPLOYMENT STATUS 📊"
echo -e "======================================${NC}"
echo ""

docker compose -f Docker/docker-compose.yml ps









echo ""
echo -e "${BLUE}Container Health:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep medihub

echo ""
echo -e "${BLUE}====================================="
echo -e "       SERVICE URLs 🌐"
echo -e "=====================================${NC}"

# read credentials from .env
PG_USER=$(grep  '^POSTGRES_USER='         .env | cut -d= -f2)
PG_PASS=$(grep  '^POSTGRES_PASSWORD='     .env | cut -d= -f2)
PG_DB=$(grep    '^POSTGRES_DB='           .env | cut -d= -f2)
RMQ_USER=$(grep '^RABBITMQ_DEFAULT_USER=' .env | cut -d= -f2)
RMQ_PASS=$(grep '^RABBITMQ_DEFAULT_PASS=' .env | cut -d= -f2)
GF_PASS="medihub_grafana"
PGA_EMAIL="admin@medihub.com"
PGA_PASS="medihub_pgadmin"

echo -e "${GREEN}App (Nginx):${NC}        http://localhost:8080"
echo -e "${GREEN}Web1:${NC}               http://localhost:8011"
echo -e "${GREEN}Web2:${NC}               http://localhost:8012"
echo -e "${GREEN}Web3:${NC}               http://localhost:8013"
echo -e "${GREEN}Swagger:${NC}            http://localhost:8080/swagger/"
echo ""
echo -e "${BLUE}--- Credentials ---${NC}"
echo -e "${GREEN}RabbitMQ UI:${NC}        http://localhost:15672"
echo -e "         user: ${YELLOW}${RMQ_USER}${NC}  pass: ${YELLOW}${RMQ_PASS}${NC}"
echo ""
echo -e "${GREEN}pgAdmin:${NC}            http://localhost:5050"
echo -e "         email: ${YELLOW}${PGA_EMAIL}${NC}  pass: ${YELLOW}${PGA_PASS}${NC}"
echo -e "         DB host: ${YELLOW}db${NC}  user: ${YELLOW}${PG_USER}${NC}  pass: ${YELLOW}${PG_PASS}${NC}  db: ${YELLOW}${PG_DB}${NC}"
echo ""
echo -e "${GREEN}Grafana:${NC}            http://localhost:3000"
echo -e "         user: ${YELLOW}admin${NC}  pass: ${YELLOW}${GF_PASS}${NC}"
echo ""
echo -e "${GREEN}Prometheus:${NC}         http://localhost:9090"
echo -e "${GREEN}Alertmanager:${NC}       http://localhost:9093"
echo -e "${GREEN}Jaeger UI:${NC}          http://localhost:16686"
echo -e "${GREEN}cAdvisor:${NC}           http://localhost:8081"
echo -e "${GREEN}Node Exporter:${NC}      http://localhost:9100"
echo -e "${GREEN}Loki:${NC}               http://localhost:3100"


echo ""
echo -e "${GREEN}======================================"
echo "May Allah give you Strength, Knowledge,"
echo "Patience and Success. Thanks 🤲"
echo "======================================"
echo -e "${NC}"
