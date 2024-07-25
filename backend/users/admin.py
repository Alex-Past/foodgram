from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email')
    list_display_links = ('username',)
    empty_value_display = 'Не задано'


admin.site.register(User, UserAdmin)
