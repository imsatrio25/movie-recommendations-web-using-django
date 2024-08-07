from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie
from .utils import get_recommendations

def recommend_movies(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        title = request.POST.get('title')
        recommendations = get_recommendations(title)
        error_message = None
        if not recommendations:
            error_message = f"No recommendations found for '{title}'"
        
        context = {
            'recommendations': recommendations,
            'error_message': error_message,
        }
        return render(request, 'recommendations/recommendations_fragment.html', context)
    
    # Initial page load
    return render(request, 'recommendations/recommend_movies.html')

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET['term']
        movies = Movie.objects.filter(original_title__icontains=term)
        titles = [movie.original_title for movie in movies]
        return JsonResponse(titles, safe=False)
    return JsonResponse([], safe=False)
