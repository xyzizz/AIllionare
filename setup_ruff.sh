#!/bin/bash
# Script to set up Ruff for Python code formatting and linting

echo "Setting up Ruff for code formatting and linting..."

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip could not be found. Please install Python and pip first."
    exit 1
fi

# Install pre-commit and ruff
echo "Installing pre-commit and ruff..."
pip install pre-commit ruff

# Install the pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to check configuration
echo "Running pre-commit on all files to validate the setup..."
pre-commit run --all-files

echo "Setup complete! Ruff and pre-commit are now configured for the project."
echo "Ruff will automatically format your code when you commit changes."
echo ""
echo "You can also run the formatter manually with: pre-commit run --all-files" 