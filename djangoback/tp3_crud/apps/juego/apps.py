import json
import os
from django.db.utils import OperationalError
from django.apps import AppConfig


class JuegoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.juego'

    def ready(self):
        from apps.juego.models import Juego
        from django.db import connection

        try:
            if not Juego.objects.exists():
                ruta_json = os.path.join(os.path.dirname(__file__), "fixtures", "vgsales.json")
                with open(ruta_json, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                    for juego_data in datos:
                        Juego.objects.create(**juego_data)
        except OperationalError:
            pass
