from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings
from workers.aggregation import run_aggregation_pipeline
from workers.detection import run_detection_pipeline
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the background scheduler for ETL and detection pipelines"""
    
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled")
        return
    
    try:
        # Schedule aggregation job
        scheduler.add_job(
            func=run_aggregation_pipeline,
            trigger=CronTrigger.from_crontab(settings.AGGREGATION_CRON),
            id='aggregation_job',
            name='Daily Aggregation Pipeline',
            replace_existing=True
        )
        logger.info(f"Aggregation job scheduled: {settings.AGGREGATION_CRON}")
        
        # Schedule detection job
        scheduler.add_job(
            func=run_detection_pipeline,
            trigger=CronTrigger.from_crontab(settings.DETECTION_CRON),
            id='detection_job',
            name='Daily Anomaly Detection Pipeline',
            replace_existing=True
        )
        logger.info(f"Detection job scheduled: {settings.DETECTION_CRON}")
        
        # Start scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
