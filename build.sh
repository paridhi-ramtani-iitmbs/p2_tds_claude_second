#!/usr/bin/env bash
# Fast build script for Render - FIXED for pandas issue
set -o errexit

echo "🚀 Building Quiz Solver (Port 10000)..."

# Upgrade pip and setuptools
echo "📦 Upgrading build tools..."
pip install --upgrade pip setuptools wheel

# Install build dependencies first
echo "🔧 Installing build dependencies..."
pip install Cython

# Install dependencies with no cache (prevents pandas build issues)
echo "📚 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Install Playwright
echo "🌐 Installing Playwright..."
playwright install-deps chromium
playwright install chromium

echo "✅ Build complete! Starting on port 10000..."
