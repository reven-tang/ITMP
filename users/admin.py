from django.contrib import admin
from .models import User

# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    list_display = ['username', 'nickname', 'last_name', 'first_name', 'email', 'is_superuser', "is_active", "is_staff"]

admin.site.register(User, UsersAdmin)
