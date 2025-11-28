# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (or Docker)

## Installation

### Option 1: Automated Setup (Recommended)

Run the setup script:

```powershell
.\setup.ps1
```

This will automatically install all backend and frontend dependencies.

### Option 2: Manual Setup

**Backend:**
```powershell
cd backend
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

## Running the Application

### 1. Start MongoDB

Using Docker:
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Or use Docker Compose:
```powershell
docker-compose up -d
```

### 2. Generate Synthetic Data

```powershell
cd scripts
python simulate_data.py --days 120 --outbreak 1 --export ../data/
```

This generates 120 days of synthetic data with a simulated outbreak.

### 3. Import Data to MongoDB

```powershell
python scripts/import_data.py --dir ./data
```

### 4. Start Backend Server

```powershell
cd backend
python main.py
```

Backend will run on: http://localhost:8000
API docs: http://localhost:8000/docs

### 5. Start Frontend

In a new terminal:
```powershell
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

## Environment Variables

Copy `.env.example` to `.env` and update values:

```powershell
cp .env.example .env
```

Key variables:
- `MONGODB_URI` - MongoDB connection string
- `OPENROUTER_API_KEY` - Your OpenRouter API key (already configured)
- `SMTP_*` - Email notification settings
- `TWILIO_*` - SMS/WhatsApp notification settings

## Project Structure

```
SilentEpidemicDetector/
├── backend/              # FastAPI backend
│   ├── agents/          # LangChain agents
│   ├── api/             # API endpoints
│   ├── core/            # Core utilities
│   ├── ml/              # ML detectors
│   ├── schemas/         # Pydantic models
│   └── workers/         # Background jobs
├── frontend/            # Next.js frontend
│   ├── app/             # Pages
│   ├── components/      # React components
│   └── lib/             # Utilities
├── scripts/             # Data generation scripts
└── data/                # Generated data
```

## API Endpoints

- `GET /` - API root
- `GET /health` - Health check
- `POST /ingest/hospital` - Ingest hospital data
- `POST /ingest/social` - Ingest social media data
- `POST /ingest/environment` - Ingest environmental data
- `GET /alerts/` - Get alerts
- `GET /alerts/{id}` - Get alert details
- `GET /alerts/stats/summary` - Get alert statistics

## Troubleshooting

### TypeScript Errors in Frontend

All TypeScript errors will disappear after running `npm install` in the frontend directory.

### Python Import Errors

Make sure you're in the correct directory when running Python scripts, and that all dependencies are installed:

```powershell
pip install -r backend/requirements.txt
```

### MongoDB Connection Issues

Ensure MongoDB is running:
```powershell
docker ps
```

Check logs:
```powershell
docker logs mongodb
```

### Port Already in Use

Backend (8000):
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Frontend (3000):
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## Development

### Run Tests

Backend:
```powershell
cd backend
pytest
```

Frontend:
```powershell
cd frontend
npm test
```

### Format Code

Backend:
```powershell
black backend/
```

Frontend:
```powershell
npm run lint
```

## Production Deployment

Use Docker Compose for production:

```powershell
docker-compose up -d
```

This starts:
- MongoDB
- Backend API
- Frontend web app

Access at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MongoDB: localhost:27017

## License

MIT
