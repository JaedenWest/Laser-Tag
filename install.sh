#!/usr/bin/env bash
set -e

#Install system dependencies 
sudo apt update
sudo apt install -y python3 python3-venv python3-tk python3-pip libpq-dev build-essential python3-dev libjpeg-dev zlib1g-dev

#install uv if not installed
if ! command -v uv &> /dev/null; then 
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

#sync project dependencies from pyproject.toml
uv sync

echo "Installation complete! You can run main.py to start the game."
