from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = (RecipeIngredientAdmin, )

    list_display = (
        'name',
        'author',
        'count_favorite'
    )
    search_fields = ('name', 'author')
    list_display_links = ('name', 'author',)
    list_filter = ('tags',)
    empty_value_display = 'Не задано'

    @admin.display(description='Количество в избранных')
    def count_favorite(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_display_links = ('name',)


admin.site.register(Tag)
