from django.contrib import admin
from django.urls import path, include

from api.views import redirect_to_recipe


urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('s/<str:short_link>', redirect_to_recipe, name='redirect-to-recipe'),
]
