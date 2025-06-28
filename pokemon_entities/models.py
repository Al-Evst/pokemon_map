from django.db import models


class Pokemon(models.Model):
    title = models.CharField("Название (рус)", max_length=200, blank=True)
    title_en = models.CharField("Название (англ)", max_length=200, blank=True)
    title_jp = models.CharField("Название (яп)", max_length=200, blank=True)
    image = models.ImageField("Изображение", upload_to='pokemons', blank=True, null=True)
    description = models.TextField("Описание", blank=True, null=True)

    previous_evolution = models.ForeignKey(
        'self',
        verbose_name="Из кого эволюционировал",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_evolutions'
    )

    class Meta:
        verbose_name = "Покемон"
        verbose_name_plural = "Покемоны"

    def __str__(self):
        return self.title or f"Покемон #{self.id}"


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        verbose_name="Покемон",
        on_delete=models.CASCADE,
        related_name="entities"
    )
    lat = models.FloatField("Широта", blank=True, null=True)
    lon = models.FloatField("Долгота", blank=True, null=True)
    appeared_at = models.DateTimeField("Появился в", blank=True, null=True)
    disappeared_at = models.DateTimeField("Исчез в", blank=True, null=True)

    level = models.IntegerField("Уровень", blank=True, null=True)
    health = models.IntegerField("Здоровье", blank=True, null=True)
    strength = models.IntegerField("Атака", blank=True, null=True)
    defence = models.IntegerField("Защита", blank=True, null=True)
    stamina = models.IntegerField("Выносливость", blank=True, null=True)

    class Meta:
        verbose_name = "Появление покемона"
        verbose_name_plural = "Появления покемонов"

    def __str__(self):
        pokemon_name = self.pokemon.title or f"Покемон #{self.pokemon.id}"
        return f"{pokemon_name} (lvl {self.level or '?'})"