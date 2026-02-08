.PHONY: dev backend frontend

dev: backend frontend

backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev
