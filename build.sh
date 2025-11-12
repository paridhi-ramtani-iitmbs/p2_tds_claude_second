#!/usr/bin/env bash
# Fast build script for Render
set -o errexit

echo "🚀 Building Quiz Solver (Port 10000)..."

# Upgrade pip
pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Install Playwright
echo "🌐 Installing Playwright..."
pip install playwright --quiet
playwright install-deps chromium
playwright install chromium

echo "✅ Build complete! Starting on port 10000..."
