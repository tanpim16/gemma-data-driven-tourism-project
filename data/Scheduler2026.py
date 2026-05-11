# =============================================================
# Scheduler2026.py
# Runs Export2026.py automatically every day at 16:00 (11:30 PM)
#
# HOW TO USE:
#   python3 data/Scheduler2026.py
#
# Leave this running in the background. Every day at 11:30 PM
# it will automatically export MongoDB data to a new CSV file.
#
# To run in background (so terminal stays free):
#   nohup python3 data/Scheduler2026.py > data/scheduler.log 2>&1 &
#   echo "Scheduler PID: $!" > data/scheduler.pid
# =============================================================

import schedule
import time
import subprocess
import pathlib
from datetime import datetime

PYTHON  = "/workspaces/gemma-data-driven-tourism-project/.venv/bin/python3"
SCRIPT  = "/workspaces/gemma-data-driven-tourism-project/data/Export2026.py"
LOG_DIR = pathlib.Path("/workspaces/gemma-data-driven-tourism-project/data")


def run_export():
    """Called every day at 16:00 — runs Export2026.py and logs output."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"export_log_{datetime.now().strftime('%Y-%m-%d')}.txt"

    print(f"[{now}] Starting daily export...")

    with open(log_file, "w") as log:
        result = subprocess.run(
            [PYTHON, SCRIPT],
            capture_output=True,
            text=True
        )
        log.write(result.stdout)
        log.write(result.stderr)

    if result.returncode == 0:
        print(f"[{now}] Export SUCCESS. Log: {log_file.name}")
    else:
        print(f"[{now}] Export FAILED. Check: {log_file.name}")
        print(result.stderr[:200])


# -- Schedule the job at 16:00 every day ----------------------
schedule.every().day.at("16:00").do(run_export)

print("=" * 55)
print("  Scheduler2026.py  --  Daily Export at 11:30 PM")
print("=" * 55)
print(f"  Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Next run  : {schedule.next_run()}")
print(f"  Script    : {SCRIPT}")
print(f"  Output    : {LOG_DIR}/travel_trends_export_YYYY-MM-DD.csv")
print("=" * 55)
print("  Waiting... (press Ctrl+C to stop)")
print()

while True:
    schedule.run_pending()
    time.sleep(30)   # check every 30 seconds
