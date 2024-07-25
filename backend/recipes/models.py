from django.contrib.auth import get_user_model
from django.db import models

TEXT_LENGHT = 300
NAME_LENGHT = 256
MEASUREMENT_UNIT_LENGHT = 25

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(max_length=NAME_LENGHT)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(max_length=NAME_LENGHT)
    measurement_unit = models.CharField(max_length=MEASUREMENT_UNIT_LENGHT)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=NAME_LENGHT)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/images')
    cooking_time = models.IntegerField(blank=False,)
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


class Favorites(models.Model):
    """Модель для избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class RecipeIngredient(models.Model):
    """Модель ингредиента рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=False)


class RecipeTag(models.Model):
    """Модель тега рецепта."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
