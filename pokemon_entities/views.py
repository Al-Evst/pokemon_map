from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from .models import Pokemon, PokemonEntity
import folium
from django.shortcuts import render



MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


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

    now = localtime()  

    # Показываем только активных покемонов
    active_entities = PokemonEntity.objects.select_related('pokemon').filter(
        appeared_at__lte=now,
        disappeared_at__gte=now
    )

    for entity in active_entities:
        pokemon = entity.pokemon
        if not pokemon.image:
            continue

        image_url = request.build_absolute_uri(pokemon.image.url)
        add_pokemon(folium_map, entity.lat, entity.lon, image_url)

    # Список всех покемонов (как было)
    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        img_url = request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL
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

    now = localtime()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    # добавляем на карту только активные сущности
    entities = pokemon.entities.filter(appeared_at__lte=now, disappeared_at__gte=now)
    for entity in entities:
        image_url = request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL
        add_pokemon(folium_map, entity.lat, entity.lon, image_url)

    # словарь в стиле JSON-файла
    pokemon_data = {
        'pokemon_id': pokemon.id,
        'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
    }

    # предыдущая эволюция
    if pokemon.previous_evolution:
        prev = pokemon.previous_evolution
        pokemon_data['previous_evolution'] = {
            'title_ru': prev.title,
            'pokemon_id': prev.id,
            'img_url': request.build_absolute_uri(prev.image.url) if prev.image else DEFAULT_IMAGE_URL,
        }

    # следующая эволюция (берем первую, если есть несколько)
    next_evo = pokemon.next_evolutions.first()
    if next_evo:
        pokemon_data['next_evolution'] = {
            'title_ru': next_evo.title,
            'pokemon_id': next_evo.id,
            'img_url': request.build_absolute_uri(next_evo.image.url) if next_evo.image else DEFAULT_IMAGE_URL,
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data,
    })
