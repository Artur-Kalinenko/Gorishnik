from django_cron import CronJobBase, Schedule
from django.core.management import call_command

# Периодическая задача для очистки устаревших корзин
class CleanupCartsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # Выполняется раз в сутки (60 минут * 24 часа)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cart.cleanup_carts_cron' # Уникальный идентификатор задания

    def do(self):
        # Запускаем команду очистки корзин
        call_command('cleanup_carts')