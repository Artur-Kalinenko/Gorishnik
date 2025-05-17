from django_cron import CronJobBase, Schedule
from django.core.management import call_command

class CleanupCartsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # каждый день (60 * 24)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cart.cleanup_carts_cron'

    def do(self):
        call_command('cleanup_carts')