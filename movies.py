from simplejustwatchapi.justwatch import search as justwatch_search
import tmdbsimple as tmdb
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta

load_dotenv()
tmdb.API_KEY = getenv('TMDB_API_KEY')
tmdb.ACCESS_TOKEN = getenv('TMDB_ACCESS_TOKEN')

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

