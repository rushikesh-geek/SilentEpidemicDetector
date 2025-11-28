from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from schemas.models import AlertSchema, AlertResponse
from core.database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=AlertResponse)
async def get_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    ward: Optional[str] = Query(None, description="Filter by ward"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1, description="Minimum confidence")
):
    """
    Retrieve alerts with optional filtering and pagination
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        ward: Filter by ward name
        severity: Filter by severity (low, medium, high, critical)
        status: Filter by status (active, acknowledged, resolved)
        min_confidence: Minimum confidence threshold
        
    Returns:
        Paginated list of alerts
    """
    try:
        # Build query
        query = {}
        if ward:
            query["location.ward"] = ward
        if severity:
            query["severity"] = severity
        if status:
            query["status"] = status
        if min_confidence is not None:
            query["confidence"] = {"$gte": min_confidence}
        
        # Get total count
        total = db.get_collection("alerts").count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * page_size
        cursor = db.get_collection("alerts").find(query).sort("timestamp", -1).skip(skip).limit(page_size)
        
        alerts = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            alerts.append(AlertSchema(**doc))
        
        return AlertResponse(
            alerts=alerts,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert_by_id(alert_id: str):
    """
    Get detailed information for a specific alert
    
    Args:
        alert_id: Alert identifier
        
    Returns:
        Alert details with full evidence and recommendations
    """
    try:
        alert = db.get_collection("alerts").find_one({"alert_id": alert_id})
        
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        alert["_id"] = str(alert["_id"])
        return AlertSchema(**alert)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")


@router.patch("/{alert_id}/status")
async def update_alert_status(alert_id: str, status: str):
    """
    Update the status of an alert
    
    Args:
        alert_id: Alert identifier
        status: New status (active, acknowledged, resolved)
        
    Returns:
        Updated alert
    """
    try:
        valid_statuses = ["active", "acknowledged", "resolved"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        result = db.get_collection("alerts").update_one(
            {"alert_id": alert_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        # Return updated alert
        alert = db.get_collection("alerts").find_one({"alert_id": alert_id})
        alert["_id"] = str(alert["_id"])
        
        logger.info(f"Alert {alert_id} status updated to {status}")
        
        return AlertSchema(**alert)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")


@router.get("/stats/summary")
async def get_alert_stats():
    """
    Get summary statistics for alerts
    
    Returns:
        Alert statistics including counts by severity, status, and recent trends
    """
    try:
        pipeline = [
            {
                "$facet": {
                    "by_severity": [
                        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
                    ],
                    "by_status": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                    ],
                    "by_ward": [
                        {"$group": {"_id": "$location.ward", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 10}
                    ],
                    "total": [
                        {"$count": "count"}
                    ],
                    "recent": [
                        {"$sort": {"timestamp": -1}},
                        {"$limit": 5},
                        {"$project": {"alert_id": 1, "severity": 1, "confidence": 1, "timestamp": 1}}
                    ]
                }
            }
        ]
        
        results = list(db.get_collection("alerts").aggregate(pipeline))
        
        if results:
            stats = results[0]
            return {
                "total_alerts": stats["total"][0]["count"] if stats["total"] else 0,
                "by_severity": {item["_id"]: item["count"] for item in stats["by_severity"]},
                "by_status": {item["_id"]: item["count"] for item in stats["by_status"]},
                "top_wards": [{"ward": item["_id"], "count": item["count"]} for item in stats["by_ward"]],
                "recent_alerts": stats["recent"]
            }
        
        return {
            "total_alerts": 0,
            "by_severity": {},
            "by_status": {},
            "top_wards": [],
            "recent_alerts": []
        }
    except Exception as e:
        logger.error(f"Error getting alert stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert statistics: {str(e)}")
