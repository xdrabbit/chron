#!/bin/bash

# Quick environment switcher for Chronicle frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
ENV_FILE="$FRONTEND_DIR/.env.local"

echo "Chronicle Environment Switcher"
echo ""
echo "Current setup:"
if [ -f "$ENV_FILE" ]; then
    cat "$ENV_FILE"
else
    echo "No .env.local file found"
fi

echo ""
echo "Select environment:"
echo "  1) LAN (home network) - Use 192.168.0.15 - FASTEST"
echo "  2) Remote (Tailscale) - Use Tailscale Funnel"
echo "  3) Show current config"
echo "  4) Exit"
echo ""
read -p "Choice [1-4]: " choice

case $choice in
    1)
        echo "Setting up for LAN (home network)..."
        cat > "$ENV_FILE" << 'EOF'
# LAN Development - FAST!
VITE_API_URL=http://192.168.0.15:8000
EOF
        echo "✓ Configured for LAN (192.168.0.15)"
        echo ""
        echo "Now restart Vite:"
        echo "  cd frontend && npm run dev"
        echo ""
        echo "Access from your Mac browser: http://localhost:3000"
        ;;
    2)
        echo "Setting up for Remote (Tailscale)..."
        cat > "$ENV_FILE" << 'EOF'
# Remote Access via Tailscale
VITE_API_URL=https://linuxmacmini.tail42ac25.ts.net:8000
EOF
        echo "✓ Configured for Tailscale remote access"
        echo ""
        echo "Now restart Vite:"
        echo "  cd frontend && npm run dev"
        ;;
    3)
        echo ""
        echo "Current configuration:"
        if [ -f "$ENV_FILE" ]; then
            cat "$ENV_FILE"
        else
            echo "No .env.local file (using defaults)"
        fi
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Recommendation: Use LAN (option 1) when at home for best performance!"
