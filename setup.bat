@echo off
echo ==================================
echo   LegalCopilot Setup
echo ==================================
echo.

cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit backend\.env and add your ANTHROPIC_API_KEY
    echo Get a free key at: https://console.anthropic.com
    echo.
)

cd ..\frontend
npm install

echo.
echo ==================================
echo   Setup complete!
echo ==================================
echo.
echo Terminal 1 (Backend):
echo   cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend ^&^& npm run dev
echo.
echo Then open: http://localhost:3000
pause
