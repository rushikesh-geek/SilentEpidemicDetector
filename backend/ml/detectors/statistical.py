import numpy as np
from datetime import datetime, timedelta
from core.database import db
import logging

logger = logging.getLogger(__name__)


class StatisticalDetector:
    """Statistical anomaly detection methods"""
    
    def __init__(self):
        self.z_score_threshold = 2.5
        self.cusum_threshold = 5.0
        self.ewma_alpha = 0.3
    
    def detect(self, aggregate: dict) -> dict:
        """
        Run statistical anomaly detection on an aggregate
        
        Args:
            aggregate: Daily aggregate data
            
        Returns:
            Dictionary of normalized scores (0-1)
        """
        try:
            scores = {
                "z_score": self._z_score_detection(aggregate),
                "cusum": self._cusum_detection(aggregate),
                "ewma": self._ewma_detection(aggregate)
            }
            
            return scores
            
        except Exception as e:
            logger.error(f"Statistical detection error: {e}")
            return {"z_score": 0.0, "cusum": 0.0, "ewma": 0.0}
    
    def _z_score_detection(self, aggregate: dict) -> float:
        """
        Z-score based anomaly detection
        
        Returns normalized score (0-1)
        """
        try:
            # Use pre-calculated z-score from aggregate
            z_score = aggregate.get("z_score")
            
            if z_score is None:
                return 0.0
            
            # Normalize z-score to 0-1 using sigmoid
            normalized = 1 / (1 + np.exp(-abs(z_score) / 2))
            
            return float(normalized)
            
        except Exception as e:
            logger.error(f"Z-score detection error: {e}")
            return 0.0
    
    def _cusum_detection(self, aggregate: dict) -> float:
        """
        CUSUM (Cumulative Sum) detection
        
        Returns normalized score (0-1)
        """
        try:
            ward = aggregate["location"]["ward"]
            current_date = aggregate["date"]
            
            # Get historical data (last 14 days)
            lookback_date = current_date - timedelta(days=14)
            
            historical = list(db.get_collection("daily_aggregates").find({
                "location.ward": ward,
                "date": {"$gte": lookback_date, "$lt": current_date}
            }).sort("date", 1))
            
            if len(historical) < 5:
                return 0.0
            
            # Extract event counts
            counts = [
                h.get("total_hospital_events", 0) + h.get("total_social_mentions", 0)
                for h in historical
            ]
            
            current_count = aggregate.get("total_hospital_events", 0) + \
                          aggregate.get("total_social_mentions", 0)
            
            # Calculate mean and std
            mean = np.mean(counts)
            std = np.std(counts)
            
            if std == 0:
                return 0.0
            
            # CUSUM calculation
            k = 0.5 * std  # Slack parameter
            cusum_pos = max(0, current_count - mean - k)
            
            # Normalize
            normalized = min(cusum_pos / (3 * std), 1.0)
            
            return float(normalized)
            
        except Exception as e:
            logger.error(f"CUSUM detection error: {e}")
            return 0.0
    
    def _ewma_detection(self, aggregate: dict) -> float:
        """
        EWMA (Exponentially Weighted Moving Average) detection
        
        Returns normalized score (0-1)
        """
        try:
            ward = aggregate["location"]["ward"]
            current_date = aggregate["date"]
            
            # Get historical data
            lookback_date = current_date - timedelta(days=14)
            
            historical = list(db.get_collection("daily_aggregates").find({
                "location.ward": ward,
                "date": {"$gte": lookback_date, "$lt": current_date}
            }).sort("date", 1))
            
            if len(historical) < 3:
                return 0.0
            
            # Extract event counts
            counts = [
                h.get("total_hospital_events", 0) + h.get("total_social_mentions", 0)
                for h in historical
            ]
            
            current_count = aggregate.get("total_hospital_events", 0) + \
                          aggregate.get("total_social_mentions", 0)
            
            # Calculate EWMA
            ewma = counts[0]
            for count in counts[1:]:
                ewma = self.ewma_alpha * count + (1 - self.ewma_alpha) * ewma
            
            # Calculate deviation
            std = np.std(counts)
            if std == 0:
                return 0.0
            
            deviation = abs(current_count - ewma) / std
            
            # Normalize
            normalized = 1 / (1 + np.exp(-deviation / 2))
            
            return float(normalized)
            
        except Exception as e:
            logger.error(f"EWMA detection error: {e}")
            return 0.0
