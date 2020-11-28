from django.contrib import admin
from django.apps import apps
from .models import Raw

@admin.register(Raw)
class TAdmin(admin.ModelAdmin):
    list_display = ['id','created_at', 'updated_at']
    list_display_links = list_display

models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
