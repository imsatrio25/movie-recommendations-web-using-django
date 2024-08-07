from celery import shared_task
from django.core.management import call_command

@shared_task
def fetch_movies_task(page):
    call_command('fetch_movies', page=page)
