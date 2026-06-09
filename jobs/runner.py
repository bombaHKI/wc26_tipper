
from app import app
from jobs.update_matches_job import run_job
import time
from datetime import datetime, timezone

if __name__ == "__main__":
    with app.app_context():
        while True:
            try:
                now = datetime.now(timezone.utc)
                print(f"[{now.isoformat()}] tick")
                run_job()
            except Exception as e:
                print("Error:", e)

            time.sleep(300)  # 5 minutes