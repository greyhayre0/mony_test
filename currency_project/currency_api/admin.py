from django.contrib import admin
from .models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("usd_rate", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("usd_rate",)
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
