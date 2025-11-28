import numpy as np
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from core.database import db
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LSTMAutoencoder(nn.Module):
    """LSTM Autoencoder for temporal anomaly detection"""
    
    def __init__(self, input_size=5, hidden_size=32, num_layers=2):
        super(LSTMAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        
        # Decoder
        self.decoder = nn.LSTM(
            input_size=hidden_size,
            hidden_size=input_size,
            num_layers=num_layers,
            batch_first=True
        )
    
    def forward(self, x):
        # Encode
        encoded, (hidden, cell) = self.encoder(x)
        
        # Decode
        decoded, _ = self.decoder(encoded)
        
        return decoded


class MLDetector:
    """Machine Learning based anomaly detectors"""
    
    def __init__(self):
        self.lstm_model = None
        self.isolation_forest = None
        self.sequence_length = 7  # 7-day sequences
        
        # Try to load pre-trained models
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if available"""
        try:
            model_path = Path("ml/saved_models")
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize LSTM Autoencoder
            self.lstm_model = LSTMAutoencoder()
            
            lstm_path = model_path / "lstm_autoencoder.pth"
            if lstm_path.exists():
                self.lstm_model.load_state_dict(torch.load(lstm_path))
                logger.info("Loaded pre-trained LSTM model")
            
            self.lstm_model.eval()
            
            # Initialize Isolation Forest
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}")
    
    def detect(self, aggregate: dict) -> dict:
        """
        Run ML-based anomaly detection
        
        Args:
            aggregate: Daily aggregate data
            
        Returns:
            Dictionary of normalized scores (0-1)
        """
        try:
            scores = {
                "lstm_autoencoder": self._lstm_detection(aggregate),
                "isolation_forest": self._isolation_forest_detection(aggregate),
                "prophet_residual": self._prophet_detection(aggregate)
            }
            
            return scores
            
        except Exception as e:
            logger.error(f"ML detection error: {e}")
            return {
                "lstm_autoencoder": 0.0,
                "isolation_forest": 0.0,
                "prophet_residual": 0.0
            }
    
    def _lstm_detection(self, aggregate: dict) -> float:
        """
        LSTM Autoencoder anomaly detection
        
        Returns normalized reconstruction error (0-1)
        """
        try:
            if self.lstm_model is None:
                return 0.0
            
            ward = aggregate["location"]["ward"]
            current_date = aggregate["date"]
            
            # Get sequence of historical data
            lookback_date = current_date - timedelta(days=self.sequence_length)
            
            historical = list(db.get_collection("daily_aggregates").find({
                "location.ward": ward,
                "date": {"$gte": lookback_date, "$lt": current_date}
            }).sort("date", 1))
            
            if len(historical) < self.sequence_length:
                return 0.0
            
            # Prepare features
            features = []
            for h in historical[-self.sequence_length:]:
                feat = [
                    h.get("total_hospital_events", 0),
                    h.get("total_social_mentions", 0),
                    h.get("environmental_risk_score", 0),
                    len(h.get("symptom_counts", {})),
                    len(h.get("social_keyword_counts", {}))
                ]
                features.append(feat)
            
            # Convert to tensor
            x = torch.FloatTensor(features).unsqueeze(0)  # Add batch dimension
            
            # Get reconstruction
            with torch.no_grad():
                reconstruction = self.lstm_model(x)
            
            # Calculate reconstruction error
            mse = torch.mean((x - reconstruction) ** 2).item()
            
            # Normalize (using typical range)
            normalized = min(mse / 100, 1.0)
            
            return float(normalized)
            
        except Exception as e:
            logger.error(f"LSTM detection error: {e}")
            return 0.0
    
    def _isolation_forest_detection(self, aggregate: dict) -> float:
        """
        Isolation Forest anomaly detection
        
        Returns normalized anomaly score (0-1)
        """
        try:
            ward = aggregate["location"]["ward"]
            current_date = aggregate["date"]
            
            # Get historical data for training
            lookback_date = current_date - timedelta(days=30)
            
            historical = list(db.get_collection("daily_aggregates").find({
                "location.ward": ward,
                "date": {"$gte": lookback_date, "$lt": current_date}
            }))
            
            if len(historical) < 10:
                return 0.0
            
            # Prepare features
            X_train = []
            for h in historical:
                feat = [
                    h.get("total_hospital_events", 0),
                    h.get("total_social_mentions", 0),
                    h.get("environmental_risk_score", 0),
                    len(h.get("symptom_counts", {})),
                    len(h.get("social_keyword_counts", {}))
                ]
                X_train.append(feat)
            
            # Current point
            current_feat = [
                aggregate.get("total_hospital_events", 0),
                aggregate.get("total_social_mentions", 0),
                aggregate.get("environmental_risk_score", 0),
                len(aggregate.get("symptom_counts", {})),
                len(aggregate.get("social_keyword_counts", {}))
            ]
            
            # Fit and predict
            self.isolation_forest.fit(X_train)
            score = self.isolation_forest.score_samples([current_feat])[0]
            
            # Normalize score (-1 to 1 range) to (0 to 1)
            normalized = (1 - score) / 2
            
            return float(max(0, min(normalized, 1)))
            
        except Exception as e:
            logger.error(f"Isolation Forest detection error: {e}")
            return 0.0
    
    def _prophet_detection(self, aggregate: dict) -> float:
        """
        Prophet-based anomaly detection using forecast residuals
        
        Returns normalized residual score (0-1)
        """
        try:
            # This is a simplified version
            # In production, you would use Prophet for forecasting
            
            ward = aggregate["location"]["ward"]
            current_date = aggregate["date"]
            
            # Get historical data
            lookback_date = current_date - timedelta(days=30)
            
            historical = list(db.get_collection("daily_aggregates").find({
                "location.ward": ward,
                "date": {"$gte": lookback_date, "$lt": current_date}
            }).sort("date", 1))
            
            if len(historical) < 14:
                return 0.0
            
            # Extract counts
            counts = [
                h.get("total_hospital_events", 0) + h.get("total_social_mentions", 0)
                for h in historical
            ]
            
            current_count = aggregate.get("total_hospital_events", 0) + \
                          aggregate.get("total_social_mentions", 0)
            
            # Simple forecast using exponential smoothing
            alpha = 0.3
            forecast = counts[0]
            for count in counts[1:]:
                forecast = alpha * count + (1 - alpha) * forecast
            
            # Calculate residual
            residual = abs(current_count - forecast)
            
            # Normalize using historical std
            std = np.std(counts)
            if std == 0:
                return 0.0
            
            normalized = min(residual / (3 * std), 1.0)
            
            return float(normalized)
            
        except Exception as e:
            logger.error(f"Prophet detection error: {e}")
            return 0.0
