from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommend_movies, name='recommend_movies'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
