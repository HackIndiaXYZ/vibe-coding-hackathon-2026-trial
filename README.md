# vibe-coding-hackathon-2026-trial
Hackathon team repository for Trial - [hackindia-team:vibe-coding-hackathon-2026:trial]

# ClassroomAgent

A web application with a React frontend and FastAPI backend.

## Project Structure

```
classroomagent/
├── frontend/       # Vite + React
├── backend/        # FastAPI (Python)
├── .env.example
└── README.md
```

## Prerequisites

- Node.js 18+
- Python 3.10+

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` in the root and fill in the required values:

```bash
cp .env.example .env
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173.

### 3. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000.

## Running Both Together

Open two terminals and run the frontend and backend commands above simultaneously.
