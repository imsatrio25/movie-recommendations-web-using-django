from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = 'Setup periodic task for fetching movies'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )

        PeriodicTask.objects.update_or_create(
            name='Fetch movies every hour starting from page 100',
            defaults={
                'interval': schedule,
                'task': 'recommendations.tasks.fetch_movies_task',
                'kwargs': json.dumps({'page': 120}),  # Start from page 100
            },
        )

        self.stdout.write(self.style.SUCCESS('Successfully set up periodic task'))
