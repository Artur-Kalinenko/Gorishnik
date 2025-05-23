from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import VerificationCode

class Command(BaseCommand):
    help = 'Очищает устаревшие верификационные коди (старше 30 минут)'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(minutes=30)
        deleted_count, _ = VerificationCode.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f'Видалено {deleted_count} прострочених кодів'))
