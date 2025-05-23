from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Видаляє непідтверджених користувачів, які зареєстровані більше 24 годин тому'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        users_to_delete = CustomUser.objects.filter(
            is_verified=False,
            date_joined__lt=cutoff
        )
        count = users_to_delete.count()
        users_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Видалено {count} непідтверджених користувачів'))
