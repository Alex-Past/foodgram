from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from . constants import (ING_NAME_LENGHT,
                         MEASUREMENT_UNIT_LENGHT,
                         MIN_COOKING_TIME,
                         MIN_ING_AMOUNT,
                         RECIPE_NAME_LENGHT,
                         TAG_NAME_LENGHT,
                         TAG_SLUG_LENGHT,
                         TEXT_LENGHT)


User = get_user_model()


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(max_length=TAG_NAME_LENGHT, unique=True)
    slug = models.SlugField(max_length=TAG_SLUG_LENGHT, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(max_length=ING_NAME_LENGHT)
    measurement_unit = models.CharField(max_length=MEASUREMENT_UNIT_LENGHT)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ungredient'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=RECIPE_NAME_LENGHT)
    text = models.TextField(max_length=TEXT_LENGHT)
    image = models.ImageField(upload_to='recipes/images')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(
            MIN_COOKING_TIME,
            f'Значение не может быть меньше {MIN_COOKING_TIME}!'
        )]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='recipes')
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингредиента рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(
            MIN_ING_AMOUNT,
            f'Значение не может быть меньше {MIN_ING_AMOUNT}!'
        )]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe'
            )
        ]


class RecipeTag(models.Model):
    """Модель тега рецепта."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class FavotiteShoppingCartBaseModel(models.Model):
    """Базовая модель избранного и корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Favorites(FavotiteShoppingCartBaseModel):
    """Модель для избранного."""

    class Meta:
        default_related_name = 'favorites'


class ShoppingCart(FavotiteShoppingCartBaseModel):
    """Модель корзины."""

    class Meta:
        default_related_name = 'shopping_cart'
