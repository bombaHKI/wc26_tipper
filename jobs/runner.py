from app import app
from jobs.update_matches_job import run_job
import time
from datetime import datetime, timezone, timedelta

if __name__ == "__main__":
    with app.app_context():

        start = datetime.now(timezone.utc)
        duration = timedelta(minutes=24*60)

        while datetime.now(timezone.utc) - start < duration:
            try:
                now = datetime.now(timezone.utc)
                print(f"[{now.isoformat()}] tick")

                run_job()

            except Exception as e:
                print("Error:", e)

            time.sleep(300)  # 5 minutes