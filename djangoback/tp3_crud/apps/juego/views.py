from django.shortcuts import render
from django.views.generic import TemplateView

class JuegoView(TemplateView):
    name = "index"
    template_name = "index.html"