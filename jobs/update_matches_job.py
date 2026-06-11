from datetime import datetime, timezone, timedelta
import traceback
from sema import Match
from odds import update_matches
from db import session
import sqlalchemy as sa
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

def should_update_matches():
    """
    Check if there's a match that:
    - Doesn't have a score set (goals_H or goals_A is None)
    - Started more than 1.5 hours ago
    
    Returns: True if update is needed, False otherwise
    """
    try:
        now = datetime.now(timezone.utc)
        time_threshold = now - timedelta(hours=1.5)
        
        # Query for unscored matches that started more than 1.5 hours ago
        match_needs_update = session.query(Match).filter(
            (Match.goals_H.is_(None) | Match.goals_A.is_(None)),
            Match.start_date < time_threshold
        ).first()
        
        return match_needs_update is not None
    except Exception as e:
        logger.error(f"Error checking if update is needed: {e}")
        return False

def run_job():
    """
    Main job function that runs periodically.
    Only calls update_matches() if there's a match that needs scoring.
    """
    try:
        if should_update_matches():
            logger.info("Found unscored match from 1.5+ hours ago. Running update_matches()...")
            update_matches()
            logger.info("Update completed successfully.")
        else:
            logger.info("No unscored matches from 1.5+ hours ago. Skipping update.")
    except Exception as e:
        logger.error(f"Error during update_matches_job: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_job()
