#!/bin/bash
# JobAcademy LMS — Start both servers

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT TERM

echo "Starting JobAcademy LMS..."

# Start backend
cd ~/JobAcademy-webapp/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ~/JobAcademy-webapp/frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!

sleep 3
echo ""
echo "=============================="
echo "  JobAcademy LMS is running"
echo "=============================="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API docs: http://localhost:8000/docs"
echo "=============================="
echo "Press Ctrl+C to stop"
echo ""

wait
