# recommendations/management/commands/fetch_movies.py

import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from recommendations.models import Movie
import time

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'

class Command(BaseCommand):
    help = 'Fetch and update movie data from TMDB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--page',
            type=int,
            default=1,
            help='The page number to start fetching movies from'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=120,  # Timeout in seconds (30 minutes)
            help='Maximum duration to run the fetch operation'
        )

    def handle(self, *args, **options):
        page = options['page']
        timeout = options['timeout']
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                break

            response = requests.get(f'{BASE_URL}/movie/popular', params={'api_key': API_KEY, 'page': page})
            data = response.json()
            movies = data.get('results', [])
            
            if not movies:
                break
            
            for movie_data in movies:
                movie_id = movie_data['id']
                
                # Check if the movie already exists
                if Movie.objects.filter(tmdb_id=movie_id).exists():
                    self.stdout.write(self.style.WARNING(f'Movie with ID {movie_id} already exists. Skipping...'))
                    continue

                movie_details = requests.get(f'{BASE_URL}/movie/{movie_id}', params={'api_key': API_KEY}).json()
                
                genres = [genre['name'] for genre in movie_details.get('genres', [])]
                poster_path = movie_details.get('poster_path', '')

                movie, created = Movie.objects.update_or_create(
                    tmdb_id=movie_details['id'],
                    defaults={
                        'imdb_id': movie_details.get('imdb_id', ''),
                        'original_language': movie_details['original_language'],
                        'original_title': movie_details['original_title'],
                        'overview': movie_details['overview'],
                        'popularity': movie_details.get('popularity', 0),
                        'poster_path': poster_path,
                        'genres': genres,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Added movie: {movie.original_title}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated movie: {movie.original_title}'))

            page += 1
            
            if page > 1000:
                break

        self.stdout.write(self.style.SUCCESS('Successfully fetched and updated movie data'))
