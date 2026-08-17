from pathlib import Path
from datetime import datetime
import threading
import time

from django.conf import settings
from django.db import connection


def create_daily_backup():
    backup_dir = Path(settings.BASE_DIR) / "backups"
    backup_dir.mkdir(exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")
    backup_path = backup_dir / f"orderboard_backup_{date}.sqlite3"

    # Already backed up today.
    if backup_path.exists():
        return

    with connection.cursor() as cursor:
        cursor.execute(
            "VACUUM INTO %s",
            [str(backup_path)],
        )

    print(f"OrderBoard backup created: {backup_path}")


def backup_worker():
    while True:
        try:
            create_daily_backup()
        except Exception as e:
            print(f"OrderBoard backup failed: {e}")

        # Check again in 1 hour.
        time.sleep(60 * 60)


def start_backup_worker():
    thread = threading.Thread(
        target=backup_worker,
        daemon=True,
    )

    thread.start()