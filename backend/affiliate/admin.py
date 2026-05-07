from django.contrib import admin
from .models import AffiliateClick

@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'ip_address', 'clicked_at']
    list_filter = ['clicked_at', 'product__vendor']
    search_fields = ['product__name']
