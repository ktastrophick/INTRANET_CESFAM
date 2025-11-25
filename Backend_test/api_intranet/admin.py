from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'tipo', 'usuario', 'color', 'fecha_registro')
    list_filter   = ('tipo', 'usuario', 'fecha')
    search_fields = ('titulo', 'descripcion')
    ordering      = ('-fecha',)
