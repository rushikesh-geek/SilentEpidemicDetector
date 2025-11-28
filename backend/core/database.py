from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: MongoClient = None
    db: Database = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB and create indexes"""
        try:
            cls.client = MongoClient(settings.MONGODB_URI)
            cls.db = cls.client[settings.MONGODB_DB]
            cls._create_indexes()
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    def _create_indexes(cls):
        """Create necessary indexes for all collections"""
        try:
            # Hospital events indexes
            cls.db.hospital_events.create_index([("timestamp", DESCENDING)])
            cls.db.hospital_events.create_index([("location.ward", ASCENDING)])
            cls.db.hospital_events.create_index([("symptoms", ASCENDING)])

            # Social posts indexes
            cls.db.social_posts.create_index([("timestamp", DESCENDING)])
            cls.db.social_posts.create_index([("location.ward", ASCENDING)])
            cls.db.social_posts.create_index([("keywords", ASCENDING)])

            # Environment data indexes
            cls.db.environment_data.create_index([("timestamp", DESCENDING)])
            cls.db.environment_data.create_index([("location.ward", ASCENDING)])

            # Daily aggregates indexes
            cls.db.daily_aggregates.create_index([
                ("date", DESCENDING),
                ("location.ward", ASCENDING)
            ], unique=True)

            # Anomaly results indexes
            cls.db.anomaly_results.create_index([("timestamp", DESCENDING)])
            cls.db.anomaly_results.create_index([("location.ward", ASCENDING)])
            cls.db.anomaly_results.create_index([("anomaly_score", DESCENDING)])

            # Alerts indexes
            cls.db.alerts.create_index([("alert_id", ASCENDING)], unique=True)
            cls.db.alerts.create_index([("timestamp", DESCENDING)])
            cls.db.alerts.create_index([("location.ward", ASCENDING)])
            cls.db.alerts.create_index([("confidence", DESCENDING)])

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    @classmethod
    def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_collection(cls, name: str) -> Collection:
        """Get a collection by name"""
        return cls.db[name]


# Initialize database connection
db = MongoDB
