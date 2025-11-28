from datetime import datetime, timedelta
from core.database import db
from core.config import settings
from ml.detectors.statistical import StatisticalDetector
from ml.detectors.ml_models import MLDetector
from ml.detectors.fusion import FusionDetector
import logging

logger = logging.getLogger(__name__)


def run_detection_pipeline(days_back: int = 1):
    """
    Run the ML anomaly detection pipeline on daily aggregates
    
    Args:
        days_back: Number of days to process
        
    Returns:
        Summary of detection results
    """
    try:
        logger.info(f"Starting anomaly detection pipeline for last {days_back} days")
        
        # Calculate date range
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days_back)
        
        # Get daily aggregates to analyze
        aggregates = list(db.get_collection("daily_aggregates").find({
            "date": {"$gte": start_date, "$lt": end_date}
        }))
        
        if not aggregates:
            logger.warning("No aggregates found for detection")
            return {"aggregates_analyzed": 0, "anomalies_detected": 0}
        
        logger.info(f"Analyzing {len(aggregates)} aggregates")
        
        # Initialize detectors
        statistical_detector = StatisticalDetector()
        ml_detector = MLDetector()
        fusion_detector = FusionDetector()
        
        anomalies_detected = 0
        
        # Process each aggregate
        for aggregate in aggregates:
            try:
                # Run statistical detectors
                stat_scores = statistical_detector.detect(aggregate)
                
                # Run ML detectors
                ml_scores = ml_detector.detect(aggregate)
                
                # Fuse scores
                anomaly_result = fusion_detector.fuse_scores(
                    aggregate=aggregate,
                    stat_scores=stat_scores,
                    ml_scores=ml_scores
                )
                
                # Save result to database
                db.get_collection("anomaly_results").insert_one(anomaly_result)
                
                # Check if it's an anomaly
                if anomaly_result["is_anomaly"]:
                    anomalies_detected += 1
                    logger.info(
                        f"Anomaly detected in {aggregate['location']['ward']} "
                        f"(score: {anomaly_result['anomaly_score']:.3f})"
                    )
                
            except Exception as e:
                logger.error(f"Error processing aggregate: {e}")
                continue
        
        logger.info(f"Detection complete: {anomalies_detected} anomalies detected")
        
        # Trigger agent escalation if anomalies found
        if anomalies_detected > 0:
            from agents.escalation import trigger_agent_pipeline
            trigger_agent_pipeline()
        
        return {
            "aggregates_analyzed": len(aggregates),
            "anomalies_detected": anomalies_detected,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Detection pipeline failed: {e}")
        raise
