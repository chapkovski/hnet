from django.contrib import admin
from django.apps import apps
from .models import Raw,StructuredPost

@admin.register(Raw)
class TAdmin(admin.ModelAdmin):
    list_display = ['id','created_at', 'updated_at']
    list_display_links = list_display

@admin.register(StructuredPost)
class TAdmin(admin.ModelAdmin):
    list_display = ['id','created_at', 'updated_at']
    list_display_links = list_display
    fields = ['contact' , 'website', 'institution_type', 'location', 'posting_date', 'closing_date','primary_categories','secondary_categories', 'positions', 'body','calculated_link_to_origin']
    readonly_fields = [ 'primary_categories', 'secondary_categories','positions','calculated_link_to_origin','posting_date', 'closing_date',]
    def calculated_link_to_origin(self, obj):
        return obj.original.url


models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
