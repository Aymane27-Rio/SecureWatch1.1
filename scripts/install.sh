#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt >/dev/null 2>&1; then
  echo "This installer currently supports apt-based systems (Ubuntu/Kali/Debian)."
  exit 1
fi

sudo apt update
# Base utilities
sudo apt install -y jq curl lsof net-tools inotify-tools
# Security tools
sudo apt install -y rkhunter aide nmap

sudo apt install -y python3 python3-venv python3-pip
# Ubuntu-friendly firewall (Kali may use nftables directly)
sudo apt install -y ufw || true

echo "Done. Consider initializing AIDE database: sudo aideinit && sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db"
