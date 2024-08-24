from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User


class UserAdmin(UserAdmin):

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
admin.site.unregister(Group)
