from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeTag, RecipeIngredient


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):

    inlines = (RecipeTagAdmin, RecipeIngredientAdmin)

    list_display = (
        'name',
        'author',
        'count_favorite'
    )
    search_fields = ('name', 'author')
    list_display_links = ('name', 'author',)
    list_filter = ('tags',)
    empty_value_display = 'Не задано'

    def count_favorite(self, obj):
        return obj.favorites.count()

    count_favorite.short_description = 'Количество в избранных'


class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_display_links = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
