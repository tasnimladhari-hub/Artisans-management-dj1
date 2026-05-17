from django.contrib import admin
from .models import Artisan, Material, Sale

@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'specialty']
    list_filter = ['user']

# rest same...