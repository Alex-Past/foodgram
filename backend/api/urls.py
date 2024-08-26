from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagsViewSet, UserViewSet

app_name = 'api'

api_v1 = DefaultRouter()
api_v1.register('users', UserViewSet, basename='users')
api_v1.register('recipes', RecipeViewSet, basename='recipes')
api_v1.register('tags', TagsViewSet, basename='tags')
api_v1.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
