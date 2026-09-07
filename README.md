# GreenHouseDesignPatterns
Description: A modular monolith that implements a smart greenhouse control system, via React, Python and Postgresql

Preresequits:   (Versions)
Python          3.11 or higher
Node.js         20 LTS
Docker Desktop  current 
Git             any

First-time setup:
Github repo: https://github.com/PaulSimonDittert/greenhouse-project

Daily start:
Terminal 1: docker compose up -d
Terminal 2: cd backend && .venv\Scripts\Activate.ps1 && cd src && uvicorn main:app --reload --port 8000
Terminal 3: cd frontend && npm run dev

URL's:
Frontend - http://localhost:5174/
Ubicorn - http://127.0.0.1:8000/

Link to course README:
https://github.com/xamk-mire/DesignPatternsMats-2026/blob/main/README.md