#!/bin/bash
# LegalCopilot — Quick Setup Script

set -e

echo "=================================="
echo "  LegalCopilot Setup"
echo "=================================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 is required. Install from https://python.org"
    exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js 18+ is required. Install from https://nodejs.org"
    exit 1
fi

echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt -q

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit backend/.env and add your ANTHROPIC_API_KEY"
    echo "Get a free key at: https://console.anthropic.com"
    echo ""
fi

cd ../frontend
echo "Setting up frontend..."
npm install --silent

echo ""
echo "=================================="
echo "  Setup complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend && source venv/bin/activate && python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo "API docs:  http://localhost:8000/api/docs"
