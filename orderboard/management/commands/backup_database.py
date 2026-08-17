from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create a backup of the SQLite database."

    def handle(self, *args, **options):
        database_path = Path(settings.DATABASES["default"]["NAME"])

        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)

        date = datetime.now().strftime("%Y-%m-%d")
        backup_path = backup_dir / f"orderboard_backup_{date}.sqlite3"

        with connection.cursor() as cursor:
            cursor.execute(
                "VACUUM INTO %s",
                [str(backup_path)],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Backup created: {backup_path}"
            )
        )