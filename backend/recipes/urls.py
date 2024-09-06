from django.urls import path

from .views import redirect_to_recipe

app_name = 'recipes'

urlpatterns = [
    path('s/<int:pk>/', redirect_to_recipe, name='short_link'),
]
