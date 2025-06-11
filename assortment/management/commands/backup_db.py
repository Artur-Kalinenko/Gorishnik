# your_app/management/commands/backup_db.py
import os
import subprocess
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = "Сделать дамп PostgreSQL и положить его в папку backups/"

    def handle(self, *args, **options):
        # Папка относительно BASE_DIR
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Метка времени
        ts = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_{ts}.sql.gz"
        filepath = os.path.join(backup_dir, filename)

        # Настройки из DATABASES
        db_conf = settings.DATABASES["default"]
        user     = db_conf["USER"]
        name     = db_conf["NAME"]
        host     = db_conf.get("HOST", "db")
        port     = db_conf.get("PORT", "5432")
        password = db_conf.get("PASSWORD", "")

        # Формируем команду pg_dump
        cmd = (
            f"pg_dump -h {host} -p {port} -U {user} {name}"
            f" | gzip > {filepath}"
        )

        # Прокидываем пароль в PGPASSWORD, чтобы pg_dump не запрашивал его
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        # Запускаем pg_dump
        subprocess.check_call(cmd, shell=True, env=env)

        self.stdout.write(self.style.SUCCESS(f"Backup saved to {filepath}"))
