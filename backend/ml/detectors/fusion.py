import numpy as np
from datetime import datetime
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class FusionDetector:
    """Fuses multiple detector scores into unified anomaly score"""
    
    def __init__(self):
        # Weights for different detectors
        self.weights = {
            "statistical": {
                "z_score": 0.15,
                "cusum": 0.15,
                "ewma": 0.10
            },
            "ml": {
                "lstm_autoencoder": 0.25,
                "isolation_forest": 0.20,
                "prophet_residual": 0.15
            }
        }
    
    def fuse_scores(self, aggregate: dict, stat_scores: dict, ml_scores: dict) -> dict:
        """
        Fuse statistical and ML scores into unified anomaly score
        
        Args:
            aggregate: Daily aggregate data
            stat_scores: Statistical detector scores
            ml_scores: ML detector scores
            
        Returns:
            Anomaly result with unified score and metadata
        """
        try:
            # Combine all scores
            all_scores = {**stat_scores, **ml_scores}
            
            # Calculate weighted fusion score
            fusion_score = 0.0
            
            for detector, score in stat_scores.items():
                weight = self.weights["statistical"].get(detector, 0)
                fusion_score += weight * score
            
            for detector, score in ml_scores.items():
                weight = self.weights["ml"].get(detector, 0)
                fusion_score += weight * score
            
            # Determine if it's an anomaly
            is_anomaly = fusion_score >= settings.ANOMALY_THRESHOLD
            
            # Calculate confidence
            confidence = self._calculate_confidence(all_scores)
            
            # Determine severity
            severity = self._determine_severity(fusion_score, confidence)
            
            # Build result
            result = {
                "timestamp": datetime.utcnow(),
                "location": aggregate["location"],
                "anomaly_score": float(fusion_score),
                "confidence": float(confidence),
                "model_scores": {
                    "z_score": stat_scores.get("z_score"),
                    "cusum": stat_scores.get("cusum"),
                    "ewma": stat_scores.get("ewma"),
                    "lstm_autoencoder": ml_scores.get("lstm_autoencoder"),
                    "isolation_forest": ml_scores.get("isolation_forest"),
                    "prophet_residual": ml_scores.get("prophet_residual")
                },
                "is_anomaly": is_anomaly,
                "severity": severity,
                "metadata": {
                    "aggregate_date": aggregate["date"],
                    "total_hospital_events": aggregate.get("total_hospital_events", 0),
                    "total_social_mentions": aggregate.get("total_social_mentions", 0),
                    "environmental_risk_score": aggregate.get("environmental_risk_score", 0),
                    "z_score": aggregate.get("z_score"),
                    "changepoint_detected": aggregate.get("changepoint_detected", False)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Score fusion error: {e}")
            raise
    
    def _calculate_confidence(self, scores: dict) -> float:
        """
        Calculate confidence based on agreement between detectors
        
        Args:
            scores: Dictionary of all detector scores
            
        Returns:
            Confidence score (0-1)
        """
        try:
            score_values = [s for s in scores.values() if s is not None]
            
            if len(score_values) < 3:
                return 0.5  # Low confidence if few detectors
            
            # Calculate agreement (low variance = high agreement)
            mean_score = np.mean(score_values)
            std_score = np.std(score_values)
            
            # High mean with low variance = high confidence
            if std_score == 0:
                confidence = mean_score
            else:
                # Penalize high variance
                confidence = mean_score * (1 - min(std_score / 0.5, 1.0))
            
            return float(max(0, min(confidence, 1)))
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    def _determine_severity(self, anomaly_score: float, confidence: float) -> str:
        """
        Determine severity level based on anomaly score and confidence
        
        Args:
            anomaly_score: Unified anomaly score (0-1)
            confidence: Confidence score (0-1)
            
        Returns:
            Severity level: low, medium, high, critical
        """
        try:
            # Combine score and confidence
            severity_score = anomaly_score * confidence
            
            if severity_score < 0.4:
                return "low"
            elif severity_score < 0.6:
                return "medium"
            elif severity_score < 0.8:
                return "high"
            else:
                return "critical"
                
        except Exception as e:
            logger.error(f"Severity determination error: {e}")
            return "medium"
