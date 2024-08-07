import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import MultiLabelBinarizer
from .models import Movie
from django.core.cache import cache
from scipy.sparse import hstack

BATCH_SIZE = 2000

def create_tfidf_matrix():
    # Initialize an empty DataFrame to store the results
    df_list = []
    
    # Fetch movie data in batches
    for i in range(0, Movie.objects.count(), BATCH_SIZE):
        movies = Movie.objects.all()[i:i + BATCH_SIZE]
        df_batch = pd.DataFrame(list(movies.values('id', 'overview', 'genres', 'original_title', 'poster_path')))
        df_list.append(df_batch)
    
    # Concatenate all batches into a single DataFrame
    df = pd.concat(df_list, ignore_index=True)
    
    # Process the DataFrame
    tfidf = TfidfVectorizer(stop_words='english')
    df['overview'] = df['overview'].fillna('')
    tfidf_matrix = tfidf.fit_transform(df['overview'])

    df['genres'] = df['genres'].apply(lambda x: x if isinstance(x, list) else [])
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df['genres'])

    combined_matrix = hstack([tfidf_matrix, genre_matrix])
    
    return df, combined_matrix


def sanitize_cache_key(key):
    return re.sub(r'[^\w]', '_', key)


BASE_URL = 'https://image.tmdb.org/t/p/w500'

def get_recommendations(title):
    cache_key = sanitize_cache_key(f'recommendations_{title}')
    recommendations = cache.get(cache_key)
    
    if recommendations is None:
        df, combined_matrix = create_tfidf_matrix()
        
        if title not in df['original_title'].values:
            return []

        idx = df[df['original_title'] == title].index[0]
        cosine_sim = linear_kernel(combined_matrix, combined_matrix)
        
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Get 10 most similar movies
        
        recommendations = []
        for i in sim_scores:
            movie = df.iloc[i[0]]
            recommendations.append({
                'title': movie['original_title'],
                'poster_path': f"{BASE_URL}{movie['poster_path']}" if movie['poster_path'] else None
            })
        
        cache.set(cache_key, recommendations, timeout=3600)  # Cache for 1 hour
    
    return recommendations
