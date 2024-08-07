# recommendations/models.py

from django.db import models

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, default=0)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)
    original_language = models.CharField(max_length=10)
    original_title = models.CharField(max_length=255)
    overview = models.TextField()
    popularity = models.FloatField(default=0)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    genres = models.JSONField()

    def __str__(self):
        return self.original_title


class FetchMoviesState(models.Model):
    current_page = models.IntegerField(default=100)
    max_page = models.IntegerField(default=1000)