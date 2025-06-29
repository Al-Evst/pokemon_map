from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime
from .models import Pokemon, PokemonEntity
import folium

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def get_pokemon_image_url(request, pokemon):
    if pokemon.image:
        return request.build_absolute_uri(pokemon.image.url)
    return DEFAULT_IMAGE_URL


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()

    active_entities = PokemonEntity.objects.select_related('pokemon').filter(
        appeared_at__lte=current_time,
        disappeared_at__gte=current_time
    )

    for entity in active_entities:
        pokemon = entity.pokemon
        if not pokemon.image:
            continue
        image_url = get_pokemon_image_url(request, pokemon)
        add_pokemon(folium_map, entity.lat, entity.lon, image_url)

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        img_url = get_pokemon_image_url(request, pokemon)
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)
    current_time = localtime()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    entities = pokemon.entities.filter(
        appeared_at__lte=current_time,
        disappeared_at__gte=current_time
    )
    for entity in entities:
        image_url = get_pokemon_image_url(request, pokemon)
        add_pokemon(folium_map, entity.lat, entity.lon, image_url)

    pokemon_data = {
        'pokemon_id': pokemon.id,
        'img_url': get_pokemon_image_url(request, pokemon),
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
    }

    if pokemon.previous_evolution:
        predecessor = pokemon.previous_evolution
        pokemon_data['previous_evolution'] = {
            'title_ru': predecessor.title,
            'pokemon_id': predecessor.id,
            'img_url': get_pokemon_image_url(request, predecessor),
        }

    next_form = pokemon.next_evolutions.first()
    if next_form:
        pokemon_data['next_evolution'] = {
            'title_ru': next_form.title,
            'pokemon_id': next_form.id,
            'img_url': get_pokemon_image_url(request, next_form),
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data,
    })