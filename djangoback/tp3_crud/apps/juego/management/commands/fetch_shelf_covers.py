import time
from django.core.management.base import BaseCommand
from apps.juego.models import Juego
from apps.juego.igdb_api import get_full_game_detail
from apps.juego.views.juegos import SHELF_PLATFORMS


class Command(BaseCommand):
    help = 'Fetch IGDB cover images for shelf games missing Image_URL'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=5,
                            help='Games per platform (default: 5)')
        parser.add_argument('--delay', type=float, default=0.3,
                            help='Seconds between requests (default: 0.3)')
        parser.add_argument('--all', action='store_true',
                            help='Process all games without cover (slow!)')

    def handle(self, *args, **options):
        delay = options['delay']
        limit = options['limit']
        fetch_all = options['all']

        if fetch_all:
            qs = Juego.objects.filter(Image_URL__isnull=True).order_by('Rank', 'id')
        else:
            ids = []
            for plat in SHELF_PLATFORMS:
                plat_ids = list(
                    Juego.objects.filter(Platform__iexact=plat, Image_URL__isnull=True)
                    .order_by('Rank', 'id')
                    .values_list('id', flat=True)[:limit]
                )
                ids.extend(plat_ids)
            qs = Juego.objects.filter(id__in=ids)

        total = qs.count()
        self.stdout.write(f'Fetching covers for {total} games...')
        ok = 0
        fail = 0

        for juego in qs:
            igdb_id = juego.API_ID
            data = get_full_game_detail(
                igdb_id=int(igdb_id) if igdb_id and str(igdb_id).isdigit() else None,
                game_name=juego.Name,
            )
            if data and data.get('cover_url'):
                juego.Image_URL = data['cover_url']
                if data.get('igdb_id') and not juego.API_ID:
                    juego.API_ID = str(data['igdb_id'])
                juego.save(update_fields=['Image_URL', 'API_ID'])
                self.stdout.write(f'  [OK] {juego.Name}')
                ok += 1
            else:
                self.stdout.write(self.style.WARNING(f'  [--] {juego.Name} (no IGDB data)'))
                fail += 1
            time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(f'Done: {ok} updated, {fail} failed'))
