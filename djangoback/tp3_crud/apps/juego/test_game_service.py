from django.test import TestCase
from .models import Juego
from .services.game_service import game_dict, search_games, get_shelves, PLAYABLE_PLATFORMS


class GameDictTest(TestCase):
    def _make_juego(self, **kwargs):
        defaults = dict(Name='Test Game', Platform='NES', Year=1985,
                        Genre='Platform', Global_Sales=1.5)
        defaults.update(kwargs)
        return Juego(**defaults)

    def test_maps_all_fields(self):
        j = self._make_juego(id=42, Publisher='Nintendo')
        d = game_dict(j)
        self.assertEqual(d['id'], 42)
        self.assertEqual(d['name'], 'Test Game')
        self.assertEqual(d['platform'], 'NES')
        self.assertEqual(d['year'], 1985)
        self.assertEqual(d['genre'], 'Platform')
        self.assertEqual(d['publisher'], 'Nintendo')
        self.assertAlmostEqual(d['global_sales'], 1.5)

    def test_playable_flag_true_for_known_platform(self):
        d = game_dict(self._make_juego(Platform='NES'))
        self.assertTrue(d['playable'])

    def test_playable_flag_false_for_unknown_platform(self):
        d = game_dict(self._make_juego(Platform='PS5'))
        self.assertFalse(d['playable'])

    def test_null_fields_default_to_empty_string(self):
        j = self._make_juego(Name=None, Platform=None, Genre=None,
                              Publisher=None, Image_URL=None, Global_Sales=None)
        d = game_dict(j)
        self.assertEqual(d['name'], '')
        self.assertEqual(d['platform'], '')
        self.assertEqual(d['image_url'], '')
        self.assertEqual(d['global_sales'], 0)


class SearchGamesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Juego.objects.create(Name='Super Mario Bros', Platform='NES',  Year=1985, Genre='Platform', Rank=1)
        Juego.objects.create(Name='The Legend of Zelda', Platform='NES',  Year=1986, Genre='Action',   Rank=2)
        Juego.objects.create(Name='Street Fighter II',   Platform='SNES', Year=1992, Genre='Fighting', Rank=3)

    def test_search_by_name(self):
        result = search_games(q='mario')
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['games'][0]['name'], 'Super Mario Bros')

    def test_search_by_name_case_insensitive(self):
        self.assertEqual(search_games(q='MARIO')['total'], 1)

    def test_search_by_platform(self):
        result = search_games(platform='SNES')
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['games'][0]['name'], 'Street Fighter II')

    def test_search_by_genre(self):
        result = search_games(q='fighting')
        self.assertEqual(result['total'], 1)

    def test_search_by_year_range(self):
        result = search_games(year_from=1985, year_to=1986)
        self.assertEqual(result['total'], 2)

    def test_search_year_from_only(self):
        result = search_games(year_from=1990)
        self.assertEqual(result['total'], 1)

    def test_search_year_to_only(self):
        result = search_games(year_to=1985)
        self.assertEqual(result['total'], 1)

    def test_search_no_results(self):
        result = search_games(q='nonexistent_xyz')
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['games'], [])

    def test_returns_correct_mode(self):
        result = search_games(q='mario')
        self.assertEqual(result['mode'], 'search')

    def test_combined_filters(self):
        result = search_games(q='zelda', platform='NES', year_from=1986, year_to=1986)
        self.assertEqual(result['total'], 1)

    def test_pagination_page_field(self):
        result = search_games(q='mario', page=1)
        self.assertEqual(result['page'], 1)


class GetShelvesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(7):
            Juego.objects.create(Name=f'NES Game {i}', Platform='NES', Year=1985,
                                  Genre='Platform', Rank=i + 1)
        Juego.objects.create(Name='SNES Game', Platform='SNES', Year=1991,
                              Genre='Action', Rank=100)

    def test_returns_shelves_mode(self):
        result = get_shelves()
        self.assertEqual(result['mode'], 'shelves')

    def test_includes_nes_shelf(self):
        platforms = [s['platform'] for s in get_shelves()['shelves']]
        self.assertIn('NES', platforms)

    def test_shelf_capped_at_5_games(self):
        shelves = {s['platform']: s for s in get_shelves()['shelves']}
        self.assertLessEqual(len(shelves['NES']['games']), 5)

    def test_shelf_total_reflects_real_count(self):
        shelves = {s['platform']: s for s in get_shelves()['shelves']}
        self.assertEqual(shelves['NES']['total'], 7)

    def test_platforms_list_contains_existing_platforms(self):
        result = get_shelves()
        self.assertIn('NES', result['platforms'])
        self.assertIn('SNES', result['platforms'])

    def test_empty_platform_not_in_shelves(self):
        platforms = [s['platform'] for s in get_shelves()['shelves']]
        self.assertNotIn('N64', platforms)
