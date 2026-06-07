from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from ..models import Juego
from .mixins import ImagenEnriquecidaMixin
from ..services.game_service import PLAYABLE_PLATFORMS, SHELF_PLATFORMS, SHELF_LABELS


class JuegoView(LoginRequiredMixin, ImagenEnriquecidaMixin, TemplateView):
    name = "home"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(Juego.objects.all(), 5)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        self.enriquecer_imagenes(page_obj)
        context["page_obj"] = page_obj
        return context


class GeneroView(LoginRequiredMixin, ImagenEnriquecidaMixin, TemplateView):
    name = "genero"
    template_name = "genero.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genero = self.request.GET.get("genero")
        juegos_qs = Juego.objects.filter(Genre__iexact=genero) if genero else Juego.objects.none()
        paginator = Paginator(juegos_qs, 5)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        self.enriquecer_imagenes(page_obj)
        context["page_obj"] = page_obj
        context["genero_actual"] = genero
        return context


class PlataformaView(LoginRequiredMixin, ImagenEnriquecidaMixin, TemplateView):
    name = "plataforma"
    template_name = "plataforma.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plataforma = self.request.GET.get("plataforma")
        juegos_qs = Juego.objects.filter(Platform__iexact=plataforma) if plataforma else Juego.objects.none()
        paginator = Paginator(juegos_qs, 5)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        self.enriquecer_imagenes(page_obj)
        context["page_obj"] = page_obj
        context["plataforma_actual"] = plataforma
        return context


class DecadaView(LoginRequiredMixin, ImagenEnriquecidaMixin, TemplateView):
    name = "decada"
    template_name = "decada.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        decada_str = self.request.GET.get("decada")
        juegos_qs = Juego.objects.none()
        decada_actual = None
        if decada_str:
            try:
                decada = int(decada_str)
                juegos_qs = Juego.objects.filter(Year__gte=decada, Year__lt=decada + 10)
                decada_actual = decada
            except ValueError:
                pass
        paginator = Paginator(juegos_qs, 5)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        self.enriquecer_imagenes(page_obj)
        context["page_obj"] = page_obj
        context["decada_actual"] = decada_actual
        return context
