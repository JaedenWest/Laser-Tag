#!/usr/bin/env bash
set -e

#Install system dependencies 
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential libpq-dev

#install uv if not installed
if ! command -v uv &> /dev/null; then 
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

#sync project dependencies from pyproject.toml
uv sync

echo "Installation complete! You can run main.py to start the game."
