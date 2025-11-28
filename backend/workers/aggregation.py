from datetime import datetime, timedelta
from collections import defaultdict
from core.database import db
import numpy as np
import logging

logger = logging.getLogger(__name__)


def run_aggregation_pipeline(days_back: int = 1):
    """
    Run the ETL and aggregation pipeline for daily per-location aggregates
    
    Args:
        days_back: Number of days to process (default: 1 for daily runs)
        
    Returns:
        Summary of aggregation results
    """
    try:
        logger.info(f"Starting aggregation pipeline for last {days_back} days")
        
        # Calculate date range
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days_back)
        
        # Get unique wards from all data sources
        wards = set()
        
        # From hospital events
        hospital_wards = db.get_collection("hospital_events").distinct(
            "location.ward",
            {"timestamp": {"$gte": start_date, "$lt": end_date}}
        )
        wards.update(hospital_wards)
        
        # From social posts
        social_wards = db.get_collection("social_posts").distinct(
            "location.ward",
            {"timestamp": {"$gte": start_date, "$lt": end_date}}
        )
        wards.update(social_wards)
        
        # From environment data
        env_wards = db.get_collection("environment_data").distinct(
            "location.ward",
            {"timestamp": {"$gte": start_date, "$lt": end_date}}
        )
        wards.update(env_wards)
        
        logger.info(f"Processing {len(wards)} wards")
        
        aggregates_created = 0
        
        # Process each ward
        for ward in wards:
            aggregate = aggregate_ward_data(ward, start_date, end_date)
            if aggregate:
                # Upsert to database
                db.get_collection("daily_aggregates").update_one(
                    {"date": start_date, "location.ward": ward},
                    {"$set": aggregate},
                    upsert=True
                )
                aggregates_created += 1
        
        logger.info(f"Aggregation complete: {aggregates_created} aggregates created/updated")
        
        return {
            "wards_processed": len(wards),
            "aggregates_created": aggregates_created,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Aggregation pipeline failed: {e}")
        raise


def aggregate_ward_data(ward: str, start_date: datetime, end_date: datetime) -> dict:
    """
    Aggregate data for a specific ward and date
    
    Args:
        ward: Ward identifier
        start_date: Start of aggregation period
        end_date: End of aggregation period
        
    Returns:
        Aggregated data dictionary
    """
    try:
        # Initialize aggregate
        aggregate = {
            "date": start_date,
            "location": {
                "ward": ward,
                "lat": 0.0,
                "lon": 0.0
            },
            "symptom_counts": {},
            "social_keyword_counts": {},
            "total_hospital_events": 0,
            "total_social_mentions": 0,
            "environmental_risk_score": 0.0,
            "rolling_mean_7d": None,
            "rolling_std_7d": None,
            "z_score": None,
            "changepoint_detected": False,
            "metadata": {}
        }
        
        # Aggregate hospital events
        hospital_events = list(db.get_collection("hospital_events").find({
            "location.ward": ward,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }))
        
        symptom_counts = defaultdict(int)
        total_patients = 0
        
        for event in hospital_events:
            # Update location (use first event's location)
            if aggregate["location"]["lat"] == 0.0:
                aggregate["location"]["lat"] = event["location"]["lat"]
                aggregate["location"]["lon"] = event["location"]["lon"]
            
            # Count symptoms
            for symptom in event.get("symptoms", []):
                symptom_counts[symptom] += event.get("patient_count", 1)
            
            total_patients += event.get("patient_count", 1)
        
        aggregate["symptom_counts"] = dict(symptom_counts)
        aggregate["total_hospital_events"] = len(hospital_events)
        aggregate["metadata"]["total_patients"] = total_patients
        
        # Aggregate social posts
        social_posts = list(db.get_collection("social_posts").find({
            "location.ward": ward,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }))
        
        keyword_counts = defaultdict(int)
        
        for post in social_posts:
            # Update location if not set
            if aggregate["location"]["lat"] == 0.0 and "location" in post:
                aggregate["location"]["lat"] = post["location"]["lat"]
                aggregate["location"]["lon"] = post["location"]["lon"]
            
            # Count keywords
            for keyword in post.get("keywords", []):
                keyword_counts[keyword] += 1
        
        aggregate["social_keyword_counts"] = dict(keyword_counts)
        aggregate["total_social_mentions"] = len(social_posts)
        
        # Aggregate environment data
        env_data = list(db.get_collection("environment_data").find({
            "location.ward": ward,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }))
        
        if env_data:
            # Update location if not set
            if aggregate["location"]["lat"] == 0.0:
                aggregate["location"]["lat"] = env_data[0]["location"]["lat"]
                aggregate["location"]["lon"] = env_data[0]["location"]["lon"]
            
            # Calculate environmental risk score
            risk_score = calculate_environmental_risk(env_data)
            aggregate["environmental_risk_score"] = risk_score
        
        # Calculate rolling statistics (7-day window)
        rolling_stats = calculate_rolling_statistics(ward, start_date)
        aggregate.update(rolling_stats)
        
        return aggregate
        
    except Exception as e:
        logger.error(f"Error aggregating ward {ward}: {e}")
        return None


def calculate_environmental_risk(env_data: list) -> float:
    """
    Calculate environmental risk score from environmental data
    
    Args:
        env_data: List of environmental data points
        
    Returns:
        Risk score (0-10)
    """
    try:
        if not env_data:
            return 0.0
        
        # Average environmental factors
        mosquito_indices = [d.get("mosquito_index", 0) for d in env_data if d.get("mosquito_index")]
        rainfall = [d.get("rainfall", 0) for d in env_data if d.get("rainfall") is not None]
        humidity = [d.get("humidity", 50) for d in env_data if d.get("humidity") is not None]
        
        risk_score = 0.0
        
        # Mosquito index contribution (0-10 scale)
        if mosquito_indices:
            risk_score += np.mean(mosquito_indices) * 0.4
        
        # Rainfall contribution (higher rainfall = higher risk for mosquito-borne diseases)
        if rainfall:
            avg_rainfall = np.mean(rainfall)
            rainfall_risk = min(avg_rainfall / 50, 1.0) * 10  # Normalize to 0-10
            risk_score += rainfall_risk * 0.3
        
        # Humidity contribution (optimal mosquito breeding: 60-80%)
        if humidity:
            avg_humidity = np.mean(humidity)
            if 60 <= avg_humidity <= 80:
                humidity_risk = 10
            else:
                humidity_risk = max(0, 10 - abs(70 - avg_humidity) / 3)
            risk_score += humidity_risk * 0.3
        
        return min(risk_score, 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating environmental risk: {e}")
        return 0.0


def calculate_rolling_statistics(ward: str, current_date: datetime) -> dict:
    """
    Calculate 7-day rolling mean, std, and z-score
    
    Args:
        ward: Ward identifier
        current_date: Current aggregation date
        
    Returns:
        Dictionary with rolling statistics
    """
    try:
        # Get past 7 days of aggregates
        lookback_date = current_date - timedelta(days=7)
        
        past_aggregates = list(db.get_collection("daily_aggregates").find({
            "location.ward": ward,
            "date": {"$gte": lookback_date, "$lt": current_date}
        }).sort("date", 1))
        
        if len(past_aggregates) < 3:  # Need minimum data points
            return {
                "rolling_mean_7d": None,
                "rolling_std_7d": None,
                "z_score": None,
                "changepoint_detected": False
            }
        
        # Extract total event counts
        event_counts = [
            agg.get("total_hospital_events", 0) + agg.get("total_social_mentions", 0)
            for agg in past_aggregates
        ]
        
        # Calculate statistics
        mean = np.mean(event_counts)
        std = np.std(event_counts)
        
        # Get today's count (from current aggregation if available)
        today_count = 0  # Will be updated with actual count
        
        # Calculate z-score
        z_score = None
        if std > 0:
            z_score = (today_count - mean) / std
        
        # Simple changepoint detection (z-score > 2)
        changepoint_detected = bool(z_score and abs(z_score) > 2)
        
        return {
            "rolling_mean_7d": float(mean),
            "rolling_std_7d": float(std),
            "z_score": float(z_score) if z_score else None,
            "changepoint_detected": changepoint_detected
        }
        
    except Exception as e:
        logger.error(f"Error calculating rolling statistics: {e}")
        return {
            "rolling_mean_7d": None,
            "rolling_std_7d": None,
            "z_score": None,
            "changepoint_detected": False
        }
