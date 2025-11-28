from fastapi import APIRouter, HTTPException
from core.database import db
from workers.aggregation import run_aggregation_pipeline
from workers.detection import run_detection_pipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        System health status
    """
    try:
        # Check MongoDB connection
        db.client.admin.command('ping')
        
        # Get collection counts
        collections_info = {
            "hospital_events": db.get_collection("hospital_events").count_documents({}),
            "social_posts": db.get_collection("social_posts").count_documents({}),
            "environment_data": db.get_collection("environment_data").count_documents({}),
            "daily_aggregates": db.get_collection("daily_aggregates").count_documents({}),
            "anomaly_results": db.get_collection("anomaly_results").count_documents({}),
            "alerts": db.get_collection("alerts").count_documents({})
        }
        
        return {
            "status": "healthy",
            "database": "connected",
            "collections": collections_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"System unhealthy: {str(e)}")


@router.post("/run-aggregation")
async def trigger_aggregation():
    """
    Manually trigger the aggregation pipeline
    
    Returns:
        Aggregation results
    """
    try:
        logger.info("Manual aggregation triggered")
        result = run_aggregation_pipeline()
        return {
            "status": "success",
            "message": "Aggregation pipeline completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Manual aggregation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")


@router.post("/run-detection")
async def trigger_detection():
    """
    Manually trigger the anomaly detection pipeline
    
    Returns:
        Detection results
    """
    try:
        logger.info("Manual detection triggered")
        result = run_detection_pipeline()
        return {
            "status": "success",
            "message": "Detection pipeline completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Manual detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/stats")
async def get_system_stats():
    """
    Get overall system statistics
    
    Returns:
        System-wide statistics
    """
    try:
        stats = {
            "data_ingestion": {
                "hospital_events": db.get_collection("hospital_events").count_documents({}),
                "social_posts": db.get_collection("social_posts").count_documents({}),
                "environment_data": db.get_collection("environment_data").count_documents({})
            },
            "processing": {
                "daily_aggregates": db.get_collection("daily_aggregates").count_documents({}),
                "anomaly_results": db.get_collection("anomaly_results").count_documents({})
            },
            "alerts": {
                "total": db.get_collection("alerts").count_documents({}),
                "active": db.get_collection("alerts").count_documents({"status": "active"}),
                "high_priority": db.get_collection("alerts").count_documents({"severity": {"$in": ["high", "critical"]}})
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")
