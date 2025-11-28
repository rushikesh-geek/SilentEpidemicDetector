from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.database import db
from core.config import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataIntegrityAgent:
    """Agent to validate data quality and detect ingestion anomalies"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None
    
    def check_data_integrity(self, ward: str, date: datetime) -> dict:
        """
        Check data integrity for a specific ward and date
        
        Args:
            ward: Ward identifier
            date: Date to check
            
        Returns:
            Dictionary with integrity findings
        """
        try:
            findings = {
                "ward": ward,
                "date": date.isoformat(),
                "issues": [],
                "warnings": [],
                "status": "ok"
            }
            
            # Check for missing data
            missing_sources = self._check_missing_sources(ward, date)
            if missing_sources:
                findings["warnings"].append(f"Missing data from sources: {', '.join(missing_sources)}")
                findings["status"] = "warning"
            
            # Check for data gaps
            gaps = self._check_data_gaps(ward, date)
            if gaps:
                findings["warnings"].extend(gaps)
                findings["status"] = "warning"
            
            # Check for duplicate entries
            duplicates = self._check_duplicates(ward, date)
            if duplicates:
                findings["issues"].append(f"Found {duplicates} potential duplicate entries")
                findings["status"] = "issue"
            
            # Check for anomalous data patterns
            anomalies = self._check_data_anomalies(ward, date)
            if anomalies:
                findings["warnings"].extend(anomalies)
            
            # Check completeness scores
            completeness = self._calculate_completeness(ward, date)
            findings["completeness_score"] = completeness
            
            if completeness < 0.5:
                findings["status"] = "issue"
                findings["issues"].append(f"Low data completeness: {completeness*100:.1f}%")
            
            logger.info(f"Data integrity check for {ward}: {findings['status']}")
            
            return findings
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            return {
                "ward": ward,
                "date": date.isoformat(),
                "status": "error",
                "issues": [str(e)]
            }
    
    def _check_missing_sources(self, ward: str, date: datetime) -> list:
        """Check for missing data sources"""
        missing = []
        
        next_day = date + timedelta(days=1)
        
        # Check hospital events
        hospital_count = db.get_collection("hospital_events").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        if hospital_count == 0:
            missing.append("hospital")
        
        # Check social posts
        social_count = db.get_collection("social_posts").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        if social_count == 0:
            missing.append("social")
        
        # Check environment data
        env_count = db.get_collection("environment_data").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        if env_count == 0:
            missing.append("environment")
        
        return missing
    
    def _check_data_gaps(self, ward: str, date: datetime) -> list:
        """Check for temporal gaps in data"""
        gaps = []
        
        # Check last 7 days for continuity
        lookback = date - timedelta(days=7)
        
        aggregates = list(db.get_collection("daily_aggregates").find({
            "location.ward": ward,
            "date": {"$gte": lookback, "$lt": date}
        }).sort("date", 1))
        
        if len(aggregates) < 5:
            gaps.append(f"Insufficient historical data: only {len(aggregates)} days in past week")
        
        return gaps
    
    def _check_duplicates(self, ward: str, date: datetime) -> int:
        """Check for potential duplicate entries"""
        next_day = date + timedelta(days=1)
        
        # Check hospital events for duplicates by post_id
        pipeline = [
            {"$match": {
                "location.ward": ward,
                "timestamp": {"$gte": date, "$lt": next_day}
            }},
            {"$group": {
                "_id": "$hospital_id",
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 5}}}  # More than 5 from same hospital might be suspicious
        ]
        
        duplicates = list(db.get_collection("hospital_events").aggregate(pipeline))
        
        return len(duplicates)
    
    def _check_data_anomalies(self, ward: str, date: datetime) -> list:
        """Check for anomalous data patterns"""
        anomalies = []
        next_day = date + timedelta(days=1)
        
        # Check for sudden spike in events
        hospital_count = db.get_collection("hospital_events").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        
        # Get average from past week
        lookback = date - timedelta(days=7)
        past_counts = []
        
        for i in range(7):
            day_start = lookback + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            count = db.get_collection("hospital_events").count_documents({
                "location.ward": ward,
                "timestamp": {"$gte": day_start, "$lt": day_end}
            })
            past_counts.append(count)
        
        if past_counts and hospital_count > sum(past_counts) / len(past_counts) * 3:
            anomalies.append(f"Unusual spike in hospital events: {hospital_count} (avg: {sum(past_counts)/len(past_counts):.1f})")
        
        return anomalies
    
    def _calculate_completeness(self, ward: str, date: datetime) -> float:
        """Calculate data completeness score"""
        next_day = date + timedelta(days=1)
        
        scores = []
        
        # Hospital data completeness
        hospital_count = db.get_collection("hospital_events").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        scores.append(min(hospital_count / 10, 1.0))  # Expect ~10 events per day
        
        # Social data completeness
        social_count = db.get_collection("social_posts").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        scores.append(min(social_count / 20, 1.0))  # Expect ~20 posts per day
        
        # Environment data completeness
        env_count = db.get_collection("environment_data").count_documents({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        })
        scores.append(min(env_count / 5, 1.0))  # Expect ~5 readings per day
        
        return sum(scores) / len(scores) if scores else 0.0


class CrossSourceVerificationAgent:
    """Agent to confirm anomalies across multiple data sources"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL
        ) if settings.OPENROUTER_API_KEY else None
    
    def verify_anomaly(self, anomaly_result: dict) -> dict:
        """
        Verify anomaly by checking correlation across data sources
        
        Args:
            anomaly_result: Anomaly detection result
            
        Returns:
            Verification result with cross-source evidence
        """
        try:
            ward = anomaly_result["location"]["ward"]
            date = anomaly_result["metadata"]["aggregate_date"]
            
            verification = {
                "ward": ward,
                "date": date.isoformat() if isinstance(date, datetime) else date,
                "verified": False,
                "confidence_boost": 0.0,
                "evidence": {},
                "correlations": []
            }
            
            # Get data from all sources
            hospital_data = self._get_hospital_evidence(ward, date)
            social_data = self._get_social_evidence(ward, date)
            env_data = self._get_environment_evidence(ward, date)
            
            verification["evidence"] = {
                "hospital": hospital_data,
                "social": social_data,
                "environment": env_data
            }
            
            # Check correlations
            correlations_found = 0
            
            # Hospital-Social correlation
            if hospital_data["has_data"] and social_data["has_data"]:
                if self._check_symptom_correlation(hospital_data, social_data):
                    verification["correlations"].append("hospital-social symptoms match")
                    correlations_found += 1
            
            # Hospital-Environment correlation
            if hospital_data["has_data"] and env_data["has_data"]:
                if env_data["risk_score"] > 5.0:
                    verification["correlations"].append("high environmental risk supports hospital surge")
                    correlations_found += 1
            
            # All three sources present
            if hospital_data["has_data"] and social_data["has_data"] and env_data["has_data"]:
                verification["correlations"].append("all three data sources available")
                correlations_found += 1
            
            # Determine verification
            verification["verified"] = correlations_found >= 2
            verification["confidence_boost"] = min(correlations_found * 0.1, 0.3)
            
            logger.info(f"Cross-source verification for {ward}: {verification['verified']}")
            
            return verification
            
        except Exception as e:
            logger.error(f"Cross-source verification failed: {e}")
            return {
                "verified": False,
                "confidence_boost": 0.0,
                "evidence": {},
                "error": str(e)
            }
    
    def _get_hospital_evidence(self, ward: str, date: datetime) -> dict:
        """Get hospital data evidence"""
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        next_day = date + timedelta(days=1)
        
        events = list(db.get_collection("hospital_events").find({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        }))
        
        if not events:
            return {"has_data": False}
        
        # Aggregate symptoms
        all_symptoms = []
        for event in events:
            all_symptoms.extend(event.get("symptoms", []))
        
        # Count unique symptoms
        from collections import Counter
        symptom_counts = Counter(all_symptoms)
        
        return {
            "has_data": True,
            "total_events": len(events),
            "unique_symptoms": len(symptom_counts),
            "top_symptoms": dict(symptom_counts.most_common(5))
        }
    
    def _get_social_evidence(self, ward: str, date: datetime) -> dict:
        """Get social media evidence"""
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        next_day = date + timedelta(days=1)
        
        posts = list(db.get_collection("social_posts").find({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        }))
        
        if not posts:
            return {"has_data": False}
        
        # Aggregate keywords
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.get("keywords", []))
        
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        
        return {
            "has_data": True,
            "total_mentions": len(posts),
            "unique_keywords": len(keyword_counts),
            "top_keywords": dict(keyword_counts.most_common(5))
        }
    
    def _get_environment_evidence(self, ward: str, date: datetime) -> dict:
        """Get environmental evidence"""
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        next_day = date + timedelta(days=1)
        
        env_data = list(db.get_collection("environment_data").find({
            "location.ward": ward,
            "timestamp": {"$gte": date, "$lt": next_day}
        }))
        
        if not env_data:
            return {"has_data": False}
        
        # Calculate averages
        import numpy as np
        
        mosquito_indices = [d.get("mosquito_index", 0) for d in env_data if d.get("mosquito_index")]
        rainfall = [d.get("rainfall", 0) for d in env_data if d.get("rainfall") is not None]
        
        return {
            "has_data": True,
            "risk_score": np.mean(mosquito_indices) if mosquito_indices else 0,
            "avg_rainfall": np.mean(rainfall) if rainfall else 0,
            "data_points": len(env_data)
        }
    
    def _check_symptom_correlation(self, hospital_data: dict, social_data: dict) -> bool:
        """Check if hospital symptoms correlate with social keywords"""
        hospital_symptoms = set(hospital_data.get("top_symptoms", {}).keys())
        social_keywords = set(social_data.get("top_keywords", {}).keys())
        
        # Common disease keywords
        disease_keywords = {"fever", "cough", "dengue", "malaria", "flu", "sick", "illness", "chills", "headache"}
        
        # Check overlap
        hospital_disease_terms = hospital_symptoms & disease_keywords
        social_disease_terms = social_keywords & disease_keywords
        
        # If both mention disease terms, there's correlation
        return len(hospital_disease_terms) > 0 and len(social_disease_terms) > 0


class EnvironmentalRiskAgent:
    """Agent to assess environmental risk factors"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL
        ) if settings.OPENROUTER_API_KEY else None
    
    def assess_environmental_risk(self, ward: str, date: datetime) -> dict:
        """
        Assess environmental risk factors
        
        Args:
            ward: Ward identifier
            date: Date to assess
            
        Returns:
            Environmental risk assessment
        """
        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date)
            
            next_day = date + timedelta(days=1)
            
            # Get environmental data
            env_data = list(db.get_collection("environment_data").find({
                "location.ward": ward,
                "timestamp": {"$gte": date, "$lt": next_day}
            }))
            
            if not env_data:
                return {
                    "risk_level": "unknown",
                    "risk_score": 0.0,
                    "factors": [],
                    "recommendation": "No environmental data available"
                }
            
            import numpy as np
            
            # Extract metrics
            mosquito_indices = [d.get("mosquito_index", 0) for d in env_data if d.get("mosquito_index")]
            rainfall = [d.get("rainfall", 0) for d in env_data if d.get("rainfall") is not None]
            humidity = [d.get("humidity", 50) for d in env_data if d.get("humidity") is not None]
            temperature = [d.get("temperature", 25) for d in env_data if d.get("temperature")]
            
            # Calculate risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Mosquito index risk
            if mosquito_indices:
                avg_mosquito = np.mean(mosquito_indices)
                if avg_mosquito > 7:
                    risk_factors.append(f"Very high mosquito index: {avg_mosquito:.1f}/10")
                    risk_score += 3.0
                elif avg_mosquito > 5:
                    risk_factors.append(f"High mosquito index: {avg_mosquito:.1f}/10")
                    risk_score += 2.0
            
            # Rainfall risk
            if rainfall:
                avg_rainfall = np.mean(rainfall)
                if avg_rainfall > 50:
                    risk_factors.append(f"Heavy rainfall: {avg_rainfall:.1f}mm (increases mosquito breeding)")
                    risk_score += 2.0
                elif avg_rainfall > 20:
                    risk_factors.append(f"Moderate rainfall: {avg_rainfall:.1f}mm")
                    risk_score += 1.0
            
            # Humidity risk
            if humidity:
                avg_humidity = np.mean(humidity)
                if 60 <= avg_humidity <= 80:
                    risk_factors.append(f"Optimal mosquito breeding humidity: {avg_humidity:.1f}%")
                    risk_score += 2.0
            
            # Temperature risk
            if temperature:
                avg_temp = np.mean(temperature)
                if 25 <= avg_temp <= 30:
                    risk_factors.append(f"Optimal mosquito activity temperature: {avg_temp:.1f}°C")
                    risk_score += 1.0
            
            # Determine risk level
            if risk_score >= 6:
                risk_level = "critical"
            elif risk_score >= 4:
                risk_level = "high"
            elif risk_score >= 2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Generate recommendation
            if risk_level in ["high", "critical"]:
                recommendation = "High environmental risk for vector-borne diseases. Recommend increased surveillance and vector control measures."
            elif risk_level == "medium":
                recommendation = "Moderate environmental risk. Monitor situation closely."
            else:
                recommendation = "Low environmental risk currently."
            
            return {
                "risk_level": risk_level,
                "risk_score": min(risk_score, 10.0),
                "factors": risk_factors,
                "recommendation": recommendation,
                "metrics": {
                    "avg_mosquito_index": np.mean(mosquito_indices) if mosquito_indices else None,
                    "avg_rainfall": np.mean(rainfall) if rainfall else None,
                    "avg_humidity": np.mean(humidity) if humidity else None,
                    "avg_temperature": np.mean(temperature) if temperature else None
                }
            }
            
        except Exception as e:
            logger.error(f"Environmental risk assessment failed: {e}")
            return {
                "risk_level": "error",
                "risk_score": 0.0,
                "factors": [],
                "recommendation": f"Error: {str(e)}"
            }


class EscalationAgent:
    """Agent to generate alerts and trigger notifications"""
    
    def __init__(self):
        self.data_integrity_agent = DataIntegrityAgent()
        self.verification_agent = CrossSourceVerificationAgent()
        self.environmental_agent = EnvironmentalRiskAgent()
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL
        ) if settings.OPENROUTER_API_KEY else None
    
    def process_anomaly(self, anomaly_result: dict) -> dict:
        """
        Process anomaly through all agents and generate alert if needed
        
        Args:
            anomaly_result: Anomaly detection result
            
        Returns:
            Alert or None
        """
        try:
            ward = anomaly_result["location"]["ward"]
            date = anomaly_result["metadata"]["aggregate_date"]
            
            logger.info(f"Processing anomaly for {ward}")
            
            # Step 1: Check data integrity
            integrity = self.data_integrity_agent.check_data_integrity(ward, date)
            
            if integrity["status"] == "issue":
                logger.warning(f"Data integrity issues for {ward}: {integrity['issues']}")
                # Don't escalate if data quality is poor
                return None
            
            # Step 2: Cross-source verification
            verification = self.verification_agent.verify_anomaly(anomaly_result)
            
            if not verification["verified"]:
                logger.info(f"Anomaly not verified across sources for {ward}")
                # Don't escalate if not verified
                return None
            
            # Step 3: Environmental risk assessment
            env_risk = self.environmental_agent.assess_environmental_risk(ward, date)
            
            # Step 4: Calculate final confidence
            base_confidence = anomaly_result["confidence"]
            confidence_boost = verification["confidence_boost"]
            
            if env_risk["risk_level"] in ["high", "critical"]:
                confidence_boost += 0.15
            
            final_confidence = min(base_confidence + confidence_boost, 1.0)
            
            # Only create alert if confidence is high enough
            if final_confidence < settings.DETECTION_CONFIDENCE_MIN:
                logger.info(f"Confidence too low for {ward}: {final_confidence:.3f}")
                return None
            
            # Step 5: Generate recommended actions
            recommended_actions = self._generate_recommendations(
                anomaly_result,
                verification,
                env_risk
            )
            
            # Step 6: Create alert
            alert = self._create_alert(
                anomaly_result,
                final_confidence,
                verification,
                env_risk,
                recommended_actions
            )
            
            # Step 7: Save alert to database
            db.get_collection("alerts").insert_one(alert)
            
            logger.info(f"Alert created: {alert['alert_id']}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Escalation processing failed: {e}")
            return None
    
    def _generate_recommendations(self, anomaly_result: dict, verification: dict, env_risk: dict) -> list:
        """Generate recommended actions based on analysis"""
        recommendations = []
        
        severity = anomaly_result["severity"]
        
        # Medicine recommendations
        if severity in ["high", "critical"]:
            recommendations.append({
                "category": "medicine",
                "action": "Stock antipyretics (paracetamol, ibuprofen) and antimalarials",
                "priority": "high",
                "target": "pharmacy",
                "details": "Prepare for potential surge in fever cases"
            })
            
            recommendations.append({
                "category": "medicine",
                "action": "Increase inventory of oral rehydration salts (ORS) and IV fluids",
                "priority": "high",
                "target": "hospital",
                "details": "Essential for treating dehydration"
            })
        
        # Equipment recommendations
        if severity == "critical":
            recommendations.append({
                "category": "equipment",
                "action": "Prepare additional hospital beds and isolation facilities",
                "priority": "critical",
                "target": "hospital",
                "details": "Prepare for potential patient surge"
            })
        
        # Staffing recommendations
        if severity in ["high", "critical"]:
            recommendations.append({
                "category": "staffing",
                "action": "Alert on-call medical staff and prepare for extended shifts",
                "priority": "high",
                "target": "hospital",
                "details": "Ensure adequate staffing for outbreak response"
            })
        
        # Environmental control
        if env_risk["risk_level"] in ["high", "critical"]:
            recommendations.append({
                "category": "preparedness",
                "action": "Initiate vector control and mosquito eradication programs",
                "priority": "high",
                "target": "public",
                "details": "High environmental risk detected for vector-borne diseases"
            })
        
        # Pharmacy preparedness
        recommendations.append({
            "category": "preparedness",
            "action": "Alert local pharmacies to monitor medication demand patterns",
            "priority": "medium",
            "target": "pharmacy",
            "details": "Early detection of unusual medication purchases"
        })
        
        # Clinic preparedness
        recommendations.append({
            "category": "preparedness",
            "action": "Increase surveillance at primary health centers and clinics",
            "priority": "medium",
            "target": "clinic",
            "details": "Monitor for early warning signs"
        })
        
        return recommendations
    
    def _create_alert(self, anomaly_result: dict, final_confidence: float, 
                     verification: dict, env_risk: dict, recommendations: list) -> dict:
        """Create alert document"""
        from datetime import datetime
        import uuid
        
        alert_id = f"ALERT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        alert = {
            "alert_id": alert_id,
            "timestamp": datetime.utcnow(),
            "location": anomaly_result["location"],
            "confidence": final_confidence,
            "anomaly_score": anomaly_result["anomaly_score"],
            "severity": anomaly_result["severity"],
            "evidence": {
                "hospital": verification["evidence"].get("hospital", {}),
                "social": verification["evidence"].get("social", {}),
                "environment": {
                    **verification["evidence"].get("environment", {}),
                    "risk_assessment": env_risk
                },
                "model_scores": anomaly_result["model_scores"]
            },
            "recommended_actions": recommendations,
            "status": "active",
            "notified": False,
            "metadata": {
                "anomaly_result_id": str(anomaly_result.get("_id", "")),
                "verification": verification,
                "base_confidence": anomaly_result["confidence"],
                "confidence_boost": final_confidence - anomaly_result["confidence"]
            }
        }
        
        return alert


def trigger_agent_pipeline():
    """Trigger the agent pipeline for recent anomalies"""
    try:
        logger.info("Starting agent pipeline")
        
        # Get recent unprocessed anomalies
        recent_anomalies = list(db.get_collection("anomaly_results").find({
            "is_anomaly": True,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)}
        }).sort("timestamp", -1))
        
        if not recent_anomalies:
            logger.info("No anomalies to process")
            return
        
        escalation_agent = EscalationAgent()
        alerts_created = 0
        
        for anomaly in recent_anomalies:
            # Check if alert already exists for this anomaly
            existing_alert = db.get_collection("alerts").find_one({
                "location.ward": anomaly["location"]["ward"],
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=12)}
            })
            
            if existing_alert:
                logger.info(f"Alert already exists for {anomaly['location']['ward']}")
                continue
            
            # Process anomaly
            alert = escalation_agent.process_anomaly(anomaly)
            
            if alert:
                # Send notifications
                from core.notifications import notification_service
                import asyncio
                asyncio.create_task(notification_service.send_alert_notifications(alert))
                
                # Mark as notified
                db.get_collection("alerts").update_one(
                    {"alert_id": alert["alert_id"]},
                    {"$set": {"notified": True}}
                )
                
                alerts_created += 1
        
        logger.info(f"Agent pipeline complete: {alerts_created} alerts created")
        
    except Exception as e:
        logger.error(f"Agent pipeline failed: {e}")
