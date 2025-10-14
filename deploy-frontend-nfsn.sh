#!/bin/bash

# Chronicle Frontend Deployment to NearlyFreeSpeech.net
# Deploys only the static frontend files

set -e

# Configuration
SERVER_USER="xdrabbit_ritualstack"
SERVER_HOST="ssh.nyc1.nearlyfreespeech.net"
PUBLIC_PATH="/home/public"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Chronicle Frontend Deployment to NFSN${NC}"
echo "============================================"

# Step 1: Build Frontend
echo -e "\n${GREEN}Step 1: Building Frontend...${NC}"
cd frontend

if [ ! -f "package.json" ]; then
    echo -e "${YELLOW}Error: package.json not found. Are you in the right directory?${NC}"
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Building production bundle..."
npm run build

if [ ! -d "dist" ]; then
    echo -e "${YELLOW}Error: Build failed - dist folder not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"
cd ..

# Step 2: Package
echo -e "\n${GREEN}Step 2: Packaging for deployment...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="chronicle-frontend-${TIMESTAMP}.tar.gz"

tar -czf "$PACKAGE_NAME" frontend/dist

echo -e "${GREEN}✓ Package created: $PACKAGE_NAME${NC}"

# Step 3: Upload
echo -e "\n${GREEN}Step 3: Uploading to NFSN...${NC}"
echo "Server: ${SERVER_HOST}"
echo "User: ${SERVER_USER}"
echo ""

read -p "Continue with upload? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Upload to tmp
scp "$PACKAGE_NAME" ${SERVER_USER}@${SERVER_HOST}:/home/tmp/

echo -e "${GREEN}✓ Upload complete${NC}"

# Step 4: Extract on Server
echo -e "\n${GREEN}Step 4: Extracting on server...${NC}"

ssh ${SERVER_USER}@${SERVER_HOST} << EOF
    set -e
    
    echo "Backing up existing files..."
    if [ -d "${PUBLIC_PATH}/old" ]; then
        rm -rf ${PUBLIC_PATH}/old
    fi
    mkdir -p ${PUBLIC_PATH}/old
    mv ${PUBLIC_PATH}/* ${PUBLIC_PATH}/old/ 2>/dev/null || true
    
    echo "Extracting new files..."
    cd ${PUBLIC_PATH}
    tar -xzf /home/tmp/${PACKAGE_NAME} --strip-components=2
    
    echo "Setting permissions..."
    chmod -R 755 ${PUBLIC_PATH}
    
    echo "Creating .htaccess for React Router..."
    cat > ${PUBLIC_PATH}/.htaccess << 'HTACCESS'
# Enable React Router
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
HTACCESS
    
    echo "Cleaning up..."
    rm /home/tmp/${PACKAGE_NAME}
    
    echo "Deployment complete!"
EOF

echo -e "\n${GREEN}✓ Frontend deployed successfully!${NC}"
echo ""
echo "Visit: https://chronicle.ritualstack.io"
echo ""
echo "Note: Make sure your backend is running and accessible."
echo "Check frontend/.env.production for API URL configuration."

# Cleanup
read -p "Delete local package? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$PACKAGE_NAME"
    echo "Package deleted"
fi

echo -e "\n${BLUE}Deployment finished!${NC}"
