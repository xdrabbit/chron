#!/bin/bash

# Chronicle Deployment Script
# Builds and deploys Chronicle to ritualstack.io

set -e  # Exit on any error

# Configuration
SERVER_USER="xdrabbit_ritualstack"
SERVER_HOST="ssh.nyc1.nearlyfreespeech.net"
SERVER_PATH="/home/protected"  # NFSN structure
SITE_PATH="/home/public"       # Where website files go
SUBDOMAIN="chronicle"  # chronicle.ritualstack.io

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Chronicle Deployment Script${NC}"
echo "================================"

# Step 1: Build Frontend
echo -e "\n${GREEN}Step 1: Building Frontend...${NC}"
cd frontend
echo "Installing dependencies..."
npm install
echo "Building production bundle..."
npm run build

if [ ! -d "dist" ]; then
    echo -e "${YELLOW}Error: Frontend build failed - dist folder not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"
cd ..

# Step 2: Prepare Backend
echo -e "\n${GREEN}Step 2: Preparing Backend...${NC}"
cd backend

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}Error: requirements.txt not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend ready${NC}"
cd ..

# Step 3: Package for deployment
echo -e "\n${GREEN}Step 3: Creating deployment package...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="chronicle-${TIMESTAMP}.tar.gz"

tar -czf "$PACKAGE_NAME" \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='frontend/dist/test_audio.wav' \
    frontend/dist \
    backend

echo -e "${GREEN}✓ Package created: $PACKAGE_NAME${NC}"

# Step 4: Upload to server
echo -e "\n${GREEN}Step 4: Uploading to ${SERVER_HOST}...${NC}"
echo "This will upload to: ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/"

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Create directory on server if it doesn't exist
ssh ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${SERVER_PATH}"

# Upload package
scp "$PACKAGE_NAME" ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/

echo -e "${GREEN}✓ Upload complete${NC}"

# Step 5: Deploy on server
echo -e "\n${GREEN}Step 5: Deploying on server...${NC}"

ssh ${SERVER_USER}@${SERVER_HOST} << EOF
    set -e
    cd ${SERVER_PATH}
    
    echo "Extracting package..."
    tar -xzf ${PACKAGE_NAME}
    
    echo "Setting up backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    pip install -r requirements.txt
    
    echo "Backend setup complete"
    
    # Check if systemd service exists
    if [ -f "/etc/systemd/system/chronicle.service" ]; then
        echo "Restarting Chronicle service..."
        sudo systemctl restart chronicle
    else
        echo "Note: systemd service not found. You'll need to set it up manually."
        echo "See DEPLOYMENT.md for instructions."
    fi
EOF

echo -e "\n${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure Nginx for ${SUBDOMAIN}.${SERVER_HOST}"
echo "2. Set up SSL with: sudo certbot --nginx -d ${SUBDOMAIN}.${SERVER_HOST}"
echo "3. Visit https://${SUBDOMAIN}.${SERVER_HOST}"
echo ""
echo "See DEPLOYMENT.md for detailed configuration instructions."

# Cleanup
read -p "Delete deployment package locally? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$PACKAGE_NAME"
    echo "Package deleted"
fi

echo -e "\n${BLUE}Deployment script finished!${NC}"
