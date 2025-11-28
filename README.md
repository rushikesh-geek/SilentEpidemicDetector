# Silent Epidemic Detector (SED)

**AI-driven real-time outbreak detection system** with full backend, ML pipeline, agentic layer, frontend, and infrastructure.

## 🚀 Features

- **Real-time Data Ingestion**: Hospital events, social media, environmental data
- **ML Anomaly Detection**: LSTM Autoencoder, Isolation Forest, Prophet, Statistical methods
- **Agentic AI Layer**: 4 LangChain agents for validation, verification, risk assessment, and escalation
- **Multi-channel Notifications**: Email, SMS, WhatsApp alerts to hospitals, pharmacies, and clinics
- **Interactive Dashboard**: Live outbreak maps, time series charts, alert management
- **Synthetic Data Generator**: 120-day simulation with outbreak scenarios

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│   MongoDB   │
│  (Next.js)  │     │  (FastAPI)   │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼────┐  ┌────▼─────┐
              │ ML Layer │  │  Agents  │
              │          │  │(LangChain)│
              └──────────┘  └──────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- OpenAI API Key (for agents)
- Twilio Account (for SMS/WhatsApp notifications)

## 🔧 Quick Start

### 1. Clone and Configure

```bash
git clone <repository>
cd MumbaiHackss
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker

```bash
docker-compose up -d
```

Services:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- MongoDB: localhost:27017

### 3. Generate Synthetic Data

```bash
cd scripts
python simulate_data.py --days 120 --outbreak 1 --export ../data/
```

### 4. Access the Dashboard

Navigate to http://localhost:3000

## 🛠️ Manual Setup (Development)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

### Data Ingestion
- `POST /ingest/hospital` - Hospital event data
- `POST /ingest/social` - Social media posts
- `POST /ingest/environment` - Environmental data

### Analytics
- `GET /alerts` - Retrieve all alerts
- `GET /alerts/{alert_id}` - Get alert details
- `GET /aggregates` - Daily aggregated metrics

### Management
- `GET /health` - System health check
- `POST /run-detection` - Trigger manual detection

## 🧠 ML Models

1. **Statistical Detectors**
   - Z-Score anomaly detection
   - CUSUM (Cumulative Sum)
   - EWMA (Exponentially Weighted Moving Average)

2. **Machine Learning**
   - LSTM Autoencoder (temporal patterns)
   - Isolation Forest (outlier detection)
   - Prophet (time series forecasting)

3. **Fusion Layer**
   - Normalized anomaly scores (0-1)
   - Weighted ensemble scoring

## 🤖 Agentic Layer

1. **Data Integrity Agent**: Validates data quality and completeness
2. **Cross-Source Verification Agent**: Confirms anomalies across multiple data sources
3. **Environmental Risk Agent**: Correlates with mosquito indices and weather
4. **Escalation Agent**: Generates alerts and triggers notifications

## 📧 Notification System

Supports:
- **Email** (SMTP)
- **SMS** (Twilio)
- **WhatsApp** (Twilio)
- **Webhooks** (Custom endpoints)

Recipients: Hospitals, Pharmacies, Clinics

## 📁 Project Structure

```
MumbaiHackss/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── ml/                  # ML models & detectors
│   ├── agents/              # LangChain agents
│   ├── core/                # Config, database, logging
│   ├── schemas/             # Pydantic models
│   ├── workers/             # Background jobs
│   ├── main.py              # FastAPI app
│   └── Dockerfile
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities & API client
│   └── Dockerfile
├── scripts/
│   └── simulate_data.py     # Synthetic data generator
├── data/                    # Generated datasets
├── docker-compose.yml
└── README.md
```

## 🔐 Security Notes

- Never commit `.env` file
- Use strong API keys
- Enable MongoDB authentication in production
- Configure CORS properly
- Use HTTPS in production

## 📈 Monitoring

- Check logs: `docker-compose logs -f backend`
- MongoDB: Connect with MongoDB Compass
- API docs: http://localhost:8000/docs

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📞 Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ for early disease outbreak detection
