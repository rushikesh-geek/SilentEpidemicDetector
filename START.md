# 🚀 Quick Start Guide

## ✅ Setup Complete!
- ✅ All dependencies installed
- ✅ MongoDB running
- ✅ 69,494 records in database
- ✅ Ready to launch!

## 🎯 Start the System (2 Steps)

### Step 1: Start Backend (Terminal 1)
```powershell
.\start_backend.ps1
```
**Wait for:** `INFO: Application startup complete.`  
**URL:** http://localhost:8000

### Step 2: Start Frontend (Terminal 2 - New Terminal)
```powershell
.\start_frontend.ps1
```
**Wait for:** `✓ Ready in 4s`  
**URL:** http://localhost:3000

## 🌐 Access Your Dashboard

Open: **http://localhost:3000**

## 📚 Additional URLs
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## ⚡ Quick Troubleshooting

**Port already in use?**
The scripts automatically stop existing processes on ports 8000 and 3000.

**Backend won't start?**
Make sure MongoDB service is running (it should be).

**Frontend shows errors?**
Wait for backend to fully start first (look for "Application startup complete").

## 📖 Full Documentation

See **SYSTEM_READY.md** for complete system documentation.

## 🔑 Environment Setup

Make sure `.env` file exists in the root with:
```env
MONGODB_URI=mongodb://localhost:27017
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4
```

## 🎯 Next Steps

1. **Verify System**: Check dashboard shows data
2. **Monitor Alerts**: Watch for anomaly detection
3. **Test Agents**: Trigger escalation workflows
4. **Check Notifications**: Verify email/SMS/WhatsApp setup

## 📝 Important Notes

- Python 3.13.5 is installed
- Updated packages for Python 3.13 compatibility:
  - numpy 1.26.4 (was 1.24.3)
  - pymongo 4.10.1 (was 4.6.0)
  - pandas 2.2.0 (was 2.0.3)
  - scikit-learn 1.5.0 (was 1.3.2)
