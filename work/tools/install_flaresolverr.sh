#!/bin/bash
# FlareSolverr Installation Script for WSL Ubuntu
# This will install FlareSolverr to bypass Cloudflare protection

set -e

echo "========================================================================"
echo "FLARESOLVERR INSTALLATION FOR WSL UBUNTU"
echo "========================================================================"
echo ""

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    echo "❌ ERROR: This script must run in WSL Ubuntu"
    exit 1
fi

echo "✅ Running in WSL Ubuntu"
echo ""

# Step 1: Install Docker if not present
echo "📦 Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "   Installing Docker..."
    
    # Update packages
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "   ✅ Docker installed"
else
    echo "   ✅ Docker already installed"
fi

# Step 2: Start Docker service
echo ""
echo "🔧 Step 2: Starting Docker service..."
sudo service docker start
sleep 2

if sudo service docker status | grep -q "running"; then
    echo "   ✅ Docker service running"
else
    echo "   ⚠️  Docker service not running, trying to start..."
    sudo service docker restart
    sleep 3
fi

# Step 3: Pull FlareSolverr Docker image
echo ""
echo "📥 Step 3: Pulling FlareSolverr Docker image..."
sudo docker pull ghcr.io/flaresolverr/flaresolverr:latest
echo "   ✅ FlareSolverr image downloaded"

# Step 4: Start FlareSolverr container
echo ""
echo "🚀 Step 4: Starting FlareSolverr container..."

# Stop and remove existing container if present
if sudo docker ps -a | grep -q flaresolverr; then
    echo "   Removing existing FlareSolverr container..."
    sudo docker stop flaresolverr 2>/dev/null || true
    sudo docker rm flaresolverr 2>/dev/null || true
fi

# Start new container
sudo docker run -d \
    --name=flaresolverr \
    -p 8191:8191 \
    -e LOG_LEVEL=info \
    --restart unless-stopped \
    ghcr.io/flaresolverr/flaresolverr:latest

echo "   ✅ FlareSolverr container started"

# Step 5: Wait for service to be ready
echo ""
echo "⏳ Step 5: Waiting for FlareSolverr to be ready..."
sleep 5

# Test FlareSolverr
echo ""
echo "🧪 Step 6: Testing FlareSolverr..."
response=$(curl -s -X POST http://localhost:8191/v1 \
    -H "Content-Type: application/json" \
    -d '{"cmd":"sessions.list"}' || echo "FAILED")

if echo "$response" | grep -q "sessions"; then
    echo "   ✅ FlareSolverr is working!"
else
    echo "   ⚠️  FlareSolverr may not be ready yet"
    echo "   Response: $response"
fi

# Step 7: Install Python package
echo ""
echo "📦 Step 7: Installing FlareSolverr Python client..."
pip3 install flaresolverr --quiet
echo "   ✅ Python package installed"

# Final summary
echo ""
echo "========================================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "========================================================================"
echo ""
echo "FlareSolverr is now running on: http://localhost:8191"
echo ""
echo "Useful commands:"
echo "  Check status:  sudo docker ps | grep flaresolverr"
echo "  View logs:     sudo docker logs flaresolverr"
echo "  Stop:          sudo docker stop flaresolverr"
echo "  Start:         sudo docker start flaresolverr"
echo "  Restart:       sudo docker restart flaresolverr"
echo ""
echo "Next: Run the Kurdistan24 test script to verify"
echo "========================================================================"
