import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # MongoDB Settings
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "sed_db"

    # ML Configuration
    ML_MODEL_PATH: str = "./ml/saved_models"
    ANOMALY_THRESHOLD: float = 0.7
    DETECTION_CONFIDENCE_MIN: float = 0.6

    # Agent Configuration
    OPENAI_API_KEY: str = ""
    LANGCHAIN_VERBOSE: bool = True

    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "alerts@sed.system"

    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"

    # Alert Recipients
    ALERT_EMAILS: str = ""
    ALERT_PHONES: str = ""
    ALERT_WEBHOOKS: str = ""

    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    AGGREGATION_CRON: str = "0 2 * * *"
    DETECTION_CRON: str = "0 3 * * *"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_alert_emails(self) -> list[str]:
        return [e.strip() for e in self.ALERT_EMAILS.split(",") if e.strip()]

    def get_alert_phones(self) -> list[str]:
        return [p.strip() for p in self.ALERT_PHONES.split(",") if p.strip()]

    def get_alert_webhooks(self) -> list[str]:
        return [w.strip() for w in self.ALERT_WEBHOOKS.split(",") if w.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
