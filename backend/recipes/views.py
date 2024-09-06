from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from .models import Recipe


def redirect_to_recipe(request, pk):
    """Редирект на страницу рецепта."""
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'recipes/{pk}/')
    raise ValidationError(f'Рецепт с id {pk} не найден.')
