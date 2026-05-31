import logging
from ..igdb_api import get_game_data_by_name

logger = logging.getLogger(__name__)


class ImagenEnriquecidaMixin:
    def enriquecer_imagenes(self, page_obj):
        for juego in page_obj.object_list:
            api_data = get_game_data_by_name(juego.Name)
            if api_data:
                juego.Image_URL = api_data.get("Image_URL")
                try:
                    juego.save()
                except Exception as e:
                    logger.error("Error guardando %s: %s", juego.Name, e)
