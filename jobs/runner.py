from app import app
from jobs.update_matches_job import run_job
import time
from datetime import datetime, timezone, timedelta
import logging
import os

# Set up logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'jobs.log')
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    with app.app_context():

        start = datetime.now(timezone.utc)
        duration = timedelta(minutes=24*60)

        while datetime.now(timezone.utc) - start < duration:
            try:
                logger.info("tick")
                run_job()

            except Exception as e:
                logger.error(f"Error: {e}")

            time.sleep(1800)