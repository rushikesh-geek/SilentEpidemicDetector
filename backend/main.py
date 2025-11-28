from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import db
from core.logging_config import logger
from core.config import settings
from workers.scheduler import start_scheduler, stop_scheduler
from api import ingest, alerts, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Silent Epidemic Detector API...")
    
    # Connect to database
    db.connect()
    
    # Start background scheduler
    start_scheduler()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()
    db.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Silent Epidemic Detector API",
    description="AI-driven real-time outbreak detection system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(alerts.router)
app.include_router(system.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Silent Epidemic Detector API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        db.client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
