#!/bin/bash

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run the application
echo "Starting the application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
