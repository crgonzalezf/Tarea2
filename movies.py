from simplejustwatchapi.justwatch import search as justwatch_search
import tmdbsimple as tmdb
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta
import requests
import logging

load_dotenv()
tmdb.API_KEY = getenv('TMDB_API_KEY')
tmdb.ACCESS_TOKEN = getenv('TMDB_ACCESS_TOKEN')

logging.basicConfig(level=logging.INFO)

def search(movie_name):
    search = tmdb.Search()
    response = search.multi(query=movie_name, language='es-CL')

    if not search.results:
        return None

    return search.results[0]

def search_platforms(movie_name):
    results = justwatch_search(movie_name, "CL", "es")
    platforms = []

    if not results:
        return platforms

    for offer in results[0].offers:
        platforms.append({
            'name': offer.package.name,
            'icon': offer.package.icon,
            'url': offer.url,
        })

    return platforms

def get_upcoming_movies():
    """
    Consulta los próximos estrenos desde la API de TMDb.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    next_week = (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')

    discover = tmdb.Discover()
    response = discover.movie(
        primary_release_date_gte=today,
        primary_release_date_lte=next_week,
        language="es-ES",
        region="US",
    )

    if not response.get('results'):
        return []

    movies = [
        {"title": movie["title"], "release_date": movie["release_date"]}
        for movie in response["results"]
    ]
    return movies

def get_movie_trailer(movie_title):
    """
    Busca un enlace a un tráiler en YouTube basado en el título de la película.
    """
    logging.info(f"Buscando tráiler para: {movie_title}")
    search_query = f"{movie_title} tráiler oficial"
    youtube_base_url = "https://www.youtube.com/results"
    params = {"search_query": search_query}

    response = requests.get(youtube_base_url, params=params)
    if response.status_code != 200:
        logging.error(f"Error al buscar tráiler en YouTube: {response.status_code}")
        return None

    # Generar un enlace directo de búsqueda en YouTube
    youtube_link = f"https://www.youtube.com/results?search_query={movie_title.replace(' ', '+')}+tráiler+oficial"
    return youtube_link


