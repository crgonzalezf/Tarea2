from movies import search, search_platforms, get_upcoming_movies
from openai import OpenAI
from models import User
from langsmith import traceable
from movies import get_movie_trailer

def build_prompt(user: User, context: str):
    system_prompt = '''Eres un chatbot que recomienda películas, te llamas 'CineBot'.
    - Tu rol es responder recomendaciones de manera breve y concisa.
    - No repitas recomendaciones.
    '''

    # Incluir preferencias del usuario
    if user.favorite_genre:
        system_prompt += f'- El género favorito del usuario es: {user.favorite_genre}.\n'
    if user.disliked_genre:
        system_prompt += f'- El género a evitar del usuario es: {user.disliked_genre}.\n'

    if context:
        system_prompt += f'Además considera el siguiente contenido: {context}\n'

    return system_prompt

@traceable(run_type="tool", name="get_movie_trailer")
def get_movie_trailer_response(client, movie_title, user):
    
    trailer_link = get_movie_trailer(movie_title)

    if not trailer_link:
        return f"Lo siento, no pude encontrar un tráiler para {movie_title}. Intenta buscarlo manualmente en YouTube."

    return f"No puedo mostrarte directamente el trailer, pero si puedo entregarte el enlace de '{movie_title}': {trailer_link}"

@traceable(run_type="tool", name="where_to_watch")
def where_to_watch(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search_platforms(search_term)

    if not movie_or_tv_show:
        return f'No estoy seguro de dónde puedes ver esta película o serie :(, pero quizas puedes revisar en JustWatch: https://www.justwatch.com/cl/buscar?q={search_term}'

    system_prompt = build_prompt(user, str(movie_or_tv_show))

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content


@traceable(run_type="tool", name="search_movie_or_tv_show")
def search_movie_or_tv_show(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search(search_term)

    if movie_or_tv_show:
        system_prompt = build_prompt(user, str(movie_or_tv_show))
    else:
        system_prompt = build_prompt(user, '')

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content


@traceable(run_type="tool", name="get_upcoming_movies")
def get_upcoming_movies_response(client: OpenAI, user: User):
    """
    Genera una respuesta sobre próximos estrenos usando TMDb y OpenAI.
    """
    # Llama a la función de TMDb para obtener los próximos estrenos
    upcoming_movies = get_upcoming_movies()

    if not upcoming_movies:
        return "Lo siento, no encontré información sobre próximos estrenos."

    # Construir una lista de estrenos
    movies_list = "\n".join([f"- {movie['title']} (Estreno: {movie['release_date']})" for movie in upcoming_movies])
    system_prompt = build_prompt(user, f"Próximos estrenos:\n{movies_list}")

    # Preparar mensajes para OpenAI
    messages_for_llm = [{"role": "system", "content": system_prompt}]
    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    # Generar la respuesta con OpenAI
    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content

