#!/bin/bash

PEM_FILE="/c/Users/Mizan/Desktop/server/medihub_server.pem"
EC2_USER="ubuntu"
EC2_HOST="13.235.184.244"
REMOTE_DIR="~/medihub"
GITHUB_REPO="https://github.com/<your-username>/medihub.git"

SSH="ssh -i $PEM_FILE $EC2_USER@$EC2_HOST"
SSH_INTERACTIVE="ssh -i $PEM_FILE -t $EC2_USER@$EC2_HOST"

echo "🔐 Connecting to EC2..."
$SSH "echo '✅ Connected to EC2'"

echo "⚙️ Setting up EC2 instance..."
$SSH << 'EOF'
  echo "📦 Updating system..."
  sudo apt update -y && sudo apt upgrade -y

  echo "🐳 Installing Docker..."
  if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
  else
    echo "✅ Docker already installed"
  fi

  echo "🐳 Installing Docker Compose..."
  if ! command -v docker compose &> /dev/null; then
    sudo apt install -y docker-compose-plugin
    echo "✅ Docker Compose installed"
  else
    echo "✅ Docker Compose already installed"
  fi

  echo "🔧 Installing Git..."
  if ! command -v git &> /dev/null; then
    sudo apt install -y git
    echo "✅ Git installed"
  else
    echo "✅ Git already installed"
  fi

  echo "🔧 Installing other utilities..."
  sudo apt install -y curl unzip awscli

  echo "✅ Instance setup complete!"
EOF

echo "📁 Setting up medihub folder..."
$SSH << EOF
  if [ ! -d ~/medihub ]; then
    git clone $GITHUB_REPO ~/medihub
    mkdir -p ~/medihub/Docker
    echo "✅ Repo cloned"
  else
    echo "✅ Repo already exists"
  fi
EOF

read -p "📦 Copy .env to server? (y/n): " copy_env
if [ "$copy_env" == "y" ]; then
  scp -i $PEM_FILE .env $EC2_USER@$EC2_HOST:$REMOTE_DIR/.env
  echo "✅ .env copied"
fi

read -p "🐳 Copy docker-compose.yml to server? (y/n): " copy_compose
if [ "$copy_compose" == "y" ]; then
  scp -i $PEM_FILE Docker/docker-compose.yml $EC2_USER@$EC2_HOST:$REMOTE_DIR/Docker/docker-compose.yml
  echo "✅ docker-compose.yml copied"
fi

echo "🚀 Deploying on EC2..."
$SSH << 'EOF'
  cd ~/medihub
  docker pull $(grep DOCKER_IMAGE .env | cut -d '=' -f2)
  DOCKER_IMAGE=$(grep DOCKER_IMAGE .env | cut -d '=' -f2) docker compose -f Docker/docker-compose.yml up -d --no-build
  echo "✅ Deployment successful!"
EOF

echo "🖥️ Staying on server..."
$SSH_INTERACTIVE
