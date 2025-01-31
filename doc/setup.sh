#!/bin/bash

# Exit on error
set -e

echo "Setting up Price Tracker Development Environment..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed. Please install Anaconda or Miniconda first."
    exit 1
fi

# Create and activate conda environment
echo "Creating conda environment..."
conda create --name e-analytics python=3.12 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate e-analytics

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start database container
echo "Starting PostgreSQL container..."
# docker-compose up db -d
heroku login
# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Initialize database
echo "Initializing database..."
flask db upgrade

echo "Setup complete! You can now run the application with:"
echo "python run.py"
