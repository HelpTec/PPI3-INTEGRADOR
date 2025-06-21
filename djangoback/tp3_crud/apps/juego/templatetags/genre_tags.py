from django import template

register = template.Library()

@register.filter
def genre_to_class(genre_name):
    # Map genre names to the CSS classes defined in your style
    genre_class_map = {
        'Action': 'btn-accion',
        'Platform': 'btn-plataforma',
        'Racing': 'btn-carreras',
        'Role-Playing': 'btn-rpg',
        'Fighting': 'btn-lucha',
        'Shooter': 'btn-shooter',
        'Strategy': 'btn-estrategia',
        'Simulation': 'btn-simulador',
        'Sports': 'btn-deportes',
        'Puzzle': 'btn-rompecabezas',
        'Adventure': 'btn-aventura',
        'Misc': 'btn-misc',
        # Add any other genres if they have specific colors
    }
    # Return the corresponding class, or a default class if not found
    return genre_class_map.get(genre_name, 'btn-misc') # 'btn-misc' or another suitable default