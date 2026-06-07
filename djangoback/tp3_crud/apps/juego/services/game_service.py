from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Juego

PLAYABLE_PLATFORMS = {
    'NES', 'SNES', 'GB', 'GBA', 'GEN', 'N64', 'PS',
    '2600', 'GG', 'NG', 'TG16', 'SAT', 'DC', 'GC',
}

SHELF_PLATFORMS = ['NES', 'SNES', 'GB', 'GBA', 'GEN', 'N64', 'PS', 'PS2', 'DS', '2600']

SHELF_LABELS = {
    'NES':  'CLÁSICOS NES',
    'SNES': 'ERA SNES',
    'GB':   'PORTÁTILES GAME BOY',
    'GBA':  'GAME BOY ADVANCE',
    'GEN':  'VELOCIDAD GENESIS',
    'N64':  'ERA NINTENDO 64',
    'PS':   'GENERACIÓN PS1',
    'PS2':  'ERA PS2',
    'DS':   'PORTÁTILES DS',
    '2600': 'ATARI 2600',
}

PER_PAGE = 10


def game_dict(g):
    return {
        'id':           g.id,
        'name':         g.Name or '',
        'platform':     g.Platform or '',
        'year':         g.Year,
        'genre':        g.Genre or '',
        'publisher':    g.Publisher or '',
        'image_url':    g.Image_URL or '',
        'global_sales': float(g.Global_Sales) if g.Global_Sales else 0,
        'playable':     (g.Platform or '') in PLAYABLE_PLATFORMS,
    }


def search_games(q='', platform='', year_from=None, year_to=None, page=1):
    """Paginated filtered search. Returns dict with mode, games, total, pages, page."""
    qs = Juego.objects.all()
    if q:
        qs = qs.filter(
            Q(Name__icontains=q) | Q(Platform__icontains=q) | Q(Genre__icontains=q)
        )
    if platform and platform != 'all':
        qs = qs.filter(Platform__iexact=platform)
    if year_from is not None:
        qs = qs.filter(Year__gte=year_from)
    if year_to is not None:
        qs = qs.filter(Year__lte=year_to)
    qs = qs.order_by('Rank', 'id')
    paginator = Paginator(qs, PER_PAGE)
    page_obj = paginator.get_page(page)
    return {
        'mode':  'search',
        'games': [game_dict(g) for g in page_obj],
        'total': paginator.count,
        'pages': paginator.num_pages,
        'page':  page_obj.number,
    }


def get_shelves():
    """Returns shelf list (top 5 per platform) plus full platforms list."""
    all_platforms = list(
        Juego.objects.values_list('Platform', flat=True)
        .distinct().order_by('Platform')
    )
    shelves = []
    for plat in SHELF_PLATFORMS:
        if plat not in all_platforms:
            continue
        qs = Juego.objects.filter(Platform__iexact=plat).order_by('Rank', 'id')
        total = qs.count()
        games = list(qs[:5])
        if games:
            shelves.append({
                'platform': plat,
                'label':    SHELF_LABELS.get(plat, plat),
                'total':    total,
                'games':    [game_dict(g) for g in games],
            })
    return {
        'mode':      'shelves',
        'shelves':   shelves,
        'platforms': all_platforms,
    }
