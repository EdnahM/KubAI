#!/bin/bash

# Quick start script for AI Pipeline Optimizer

echo "🚀 AI-Powered Pipeline Optimizer - Quick Start"
echo "=============================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Available commands:"
echo ""
echo "  Analyze pipelines (one-time):"
echo "    python main.py --mode analyze --pipeline-type both"
echo ""
echo "  Start continuous monitoring:"
echo "    python main.py --mode monitor --pipeline-type both"
echo ""
echo "  Generate optimization suggestions:"
echo "    python main.py --mode optimize --pipeline-type both"
echo ""
echo "  Show help:"
echo "    python main.py --help"
echo ""
echo "📝 Note: Edit config/config.yaml to configure your pipeline sources"
echo ""
