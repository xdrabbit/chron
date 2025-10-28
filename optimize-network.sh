#!/bin/bash

# Network optimization script for AI request latency on remote Linux dev box
# This configures TCP keepalive and connection tuning for better performance

echo "=== Optimizing TCP settings for AI request latency ==="

# Check current TCP settings
echo -e "\n📊 Current TCP settings:"
echo "TCP keepalive time: $(cat /proc/sys/net/ipv4/tcp_keepalive_time)s"
echo "TCP keepalive interval: $(cat /proc/sys/net/ipv4/tcp_keepalive_intvl)s"
echo "TCP keepalive probes: $(cat /proc/sys/net/ipv4/tcp_keepalive_probes)"

# Temporary changes (will reset on reboot)
echo -e "\n⚡ Applying temporary TCP optimizations..."

# Reduce keepalive time from default 7200s to 60s
sudo sysctl -w net.ipv4.tcp_keepalive_time=60 2>/dev/null && echo "✓ Reduced TCP keepalive time to 60s"

# Reduce keepalive interval from 75s to 10s
sudo sysctl -w net.ipv4.tcp_keepalive_intvl=10 2>/dev/null && echo "✓ Reduced TCP keepalive interval to 10s"

# Reduce keepalive probes from 9 to 3
sudo sysctl -w net.ipv4.tcp_keepalive_probes=3 2>/dev/null && echo "✓ Reduced TCP keepalive probes to 3"

# Enable TCP Fast Open for faster connection establishment
sudo sysctl -w net.ipv4.tcp_fastopen=3 2>/dev/null && echo "✓ Enabled TCP Fast Open"

# Increase max connections
sudo sysctl -w net.core.somaxconn=1024 2>/dev/null && echo "✓ Increased max connections to 1024"

# Optimize TCP window scaling
sudo sysctl -w net.ipv4.tcp_window_scaling=1 2>/dev/null && echo "✓ Enabled TCP window scaling"

echo -e "\n✅ Temporary optimizations applied!"
echo "These settings will reset on reboot."
echo ""
echo "To make permanent, add to /etc/sysctl.conf:"
echo "  net.ipv4.tcp_keepalive_time = 60"
echo "  net.ipv4.tcp_keepalive_intvl = 10"
echo "  net.ipv4.tcp_keepalive_probes = 3"
echo "  net.ipv4.tcp_fastopen = 3"
echo "  net.core.somaxconn = 1024"
echo "  net.ipv4.tcp_window_scaling = 1"
echo ""
echo "Then run: sudo sysctl -p"
