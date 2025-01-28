from apscheduler.schedulers.background import BackgroundScheduler
from app.scrapers.run_scrapers import run_all_scrapers
import logging

# Configure logging for scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_scheduler():
    """Start the APScheduler to run the scrapers periodically."""
    scheduler = BackgroundScheduler()
    
    # Add job to run the scrapers every day at midnight
    scheduler.add_job(run_all_scrapers, 'interval', hours=3)

    # Start the scheduler
    scheduler.start()

    logger.info("Scheduler started, scrapers will run every 3 hours.")

if __name__ == '__main__':
    start_scheduler()
