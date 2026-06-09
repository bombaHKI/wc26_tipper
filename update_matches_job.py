from datetime import datetime, timezone, timedelta
from sema import Match
from odds import update_matches
from db import session
import sqlalchemy as sa

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
        print(f"Error checking if update is needed: {e}")
        return False

def run_job():
    """
    Main job function that runs periodically.
    Only calls update_matches() if there's a match that needs scoring.
    """
    try:
        if should_update_matches():
            print(f"[{datetime.now(timezone.utc)}] Found unscored match from 1.5+ hours ago. Running update_matches()...")
            update_matches()
            print(f"[{datetime.now(timezone.utc)}] Update completed successfully.")
        else:
            print(f"[{datetime.now(timezone.utc)}] No unscored matches from 1.5+ hours ago. Skipping update.")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error during update_matches_job: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_job()
