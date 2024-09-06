from django.contrib import admin
from django.urls import path, include

from api.views import ShortLinkRedirectView


urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('s/<int:pk>/',
         ShortLinkRedirectView.as_view(),
         name='recipe_short_link'),
]
