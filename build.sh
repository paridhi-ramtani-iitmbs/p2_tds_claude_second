#!/usr/bin/env bash
set -o errexit

echo "🚀 Building with pre-built wheels only..."

# Upgrade pip
python -m pip install --upgrade pip

# Install numpy and pandas with ONLY pre-built wheels (no compilation)
echo "📊 Installing data libraries..."
pip install --only-binary :all: numpy==1.24.4
pip install --only-binary :all: pandas==2.0.3

# Install other dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Playwright
echo "🌐 Installing browsers..."
playwright install-deps chromium
playwright install chromium

echo "✅ Build complete!"
