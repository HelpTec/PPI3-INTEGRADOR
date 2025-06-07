from django.contrib import admin

from apps.juego.models import Juego

@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display= (
        "Rank",
        "Name",
        "Platform",
        "Year",
        "Genre",
        "Publisher",
        "NA_Sales",
        "EU_Sales",
        "JP_Sales",
        "Other_Sales",
        "Global_Sales"    
    )
