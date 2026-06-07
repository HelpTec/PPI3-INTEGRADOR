from unittest.mock import patch, MagicMock
from django.test import TestCase
from .models import Juego
from .services.igdb_service import get_enriched_game, _get_db_similar_games

_IGDB_PATH      = 'apps.juego.services.igdb_service.get_full_game_detail'
_TRANSLATE_PATH = 'apps.juego.services.igdb_service.translate_to_spanish'


class GetEnrichedGameTest(TestCase):
    def setUp(self):
        self.juego = Juego.objects.create(
            Name='Super Mario Bros', Platform='NES', Year=1985,
            Genre='Platform', API_ID='1234',
        )

    def test_returns_none_for_missing_game(self):
        self.assertIsNone(get_enriched_game(99999))

    @patch(_IGDB_PATH, return_value=None)
    def test_returns_none_when_igdb_has_no_data(self, _mock):
        self.assertIsNone(get_enriched_game(self.juego.pk))

    @patch(_IGDB_PATH, return_value=None)
    def test_passes_api_id_to_igdb(self, mock_igdb):
        get_enriched_game(self.juego.pk)
        mock_igdb.assert_called_once_with(igdb_id=1234, game_name='Super Mario Bros')

    @patch(_IGDB_PATH, return_value=None)
    def test_passes_none_igdb_id_when_not_set(self, mock_igdb):
        self.juego.API_ID = None
        self.juego.save()
        get_enriched_game(self.juego.pk)
        mock_igdb.assert_called_once_with(igdb_id=None, game_name='Super Mario Bros')

    @patch(_TRANSLATE_PATH, return_value='Descripción en español')
    @patch(_IGDB_PATH)
    def test_translates_summary_when_not_cached(self, mock_igdb, mock_translate):
        mock_igdb.return_value = {'summary': 'English summary', 'cover_url': None}
        result = get_enriched_game(self.juego.pk)
        self.assertEqual(result['summary'], 'Descripción en español')
        mock_translate.assert_called_once_with('English summary')

    @patch(_TRANSLATE_PATH)
    @patch(_IGDB_PATH)
    def test_uses_cached_summary_without_calling_deepl(self, mock_igdb, mock_translate):
        self.juego.Summary_ES = 'Resumen en caché'
        self.juego.save()
        mock_igdb.return_value = {'summary': 'English summary', 'cover_url': None}
        result = get_enriched_game(self.juego.pk)
        self.assertEqual(result['summary'], 'Resumen en caché')
        mock_translate.assert_not_called()

    @patch(_TRANSLATE_PATH, return_value='Texto traducido')
    @patch(_IGDB_PATH)
    def test_caches_translated_summary_to_model(self, mock_igdb, _mock_translate):
        mock_igdb.return_value = {'summary': 'English', 'cover_url': None}
        get_enriched_game(self.juego.pk)
        self.juego.refresh_from_db()
        self.assertEqual(self.juego.Summary_ES, 'Texto traducido')

    @patch(_IGDB_PATH)
    def test_updates_image_url_when_changed(self, mock_igdb):
        new_url = 'https://example.com/cover.jpg'
        mock_igdb.return_value = {'cover_url': new_url, 'igdb_id': None}
        get_enriched_game(self.juego.pk)
        self.juego.refresh_from_db()
        self.assertEqual(self.juego.Image_URL, new_url)

    @patch(_IGDB_PATH)
    def test_does_not_overwrite_existing_image_url(self, mock_igdb):
        self.juego.Image_URL = 'https://existing.com/cover.jpg'
        self.juego.save()
        mock_igdb.return_value = {'cover_url': 'https://existing.com/cover.jpg', 'igdb_id': None}
        get_enriched_game(self.juego.pk)
        self.juego.refresh_from_db()
        self.assertEqual(self.juego.Image_URL, 'https://existing.com/cover.jpg')

    @patch(_IGDB_PATH)
    def test_returns_data_dict(self, mock_igdb):
        mock_igdb.return_value = {'name': 'Super Mario Bros', 'cover_url': None}
        result = get_enriched_game(self.juego.pk)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Super Mario Bros')

    @patch(_IGDB_PATH)
    def test_falls_back_to_db_similar_when_igdb_returns_none(self, mock_igdb):
        Juego.objects.create(Name='Duck Hunt', Platform='NES', Genre='Platform', Rank=10)
        mock_igdb.return_value = {'similar_games': [], 'cover_url': None}
        result = get_enriched_game(self.juego.pk)
        self.assertGreater(len(result['similar_games']), 0)
        self.assertEqual(result['similar_games'][0]['name'], 'Duck Hunt')

    @patch(_IGDB_PATH)
    def test_does_not_override_igdb_similar_games_when_present(self, mock_igdb):
        igdb_similar = [{'name': 'Metroid', 'cover_url': None}]
        mock_igdb.return_value = {'similar_games': igdb_similar, 'cover_url': None}
        result = get_enriched_game(self.juego.pk)
        self.assertEqual(result['similar_games'], igdb_similar)


class DbSimilarGamesTest(TestCase):
    def setUp(self):
        self.juego = Juego.objects.create(
            Name='Super Mario Bros', Platform='NES', Genre='Platform', Rank=1
        )
        self.same_genre_same_plat = Juego.objects.create(
            Name='Duck Hunt', Platform='NES', Genre='Platform', Rank=2
        )
        self.same_genre_diff_plat = Juego.objects.create(
            Name='Mega Man', Platform='SNES', Genre='Platform', Rank=3
        )
        self.diff_genre = Juego.objects.create(
            Name='Street Fighter', Platform='NES', Genre='Fighting', Rank=4
        )

    def test_excludes_the_game_itself(self):
        results = _get_db_similar_games(self.juego)
        ids = [g['id'] for g in results]
        self.assertNotIn(self.juego.pk, ids)

    def test_prefers_same_genre_and_platform(self):
        results = _get_db_similar_games(self.juego)
        self.assertEqual(results[0]['id'], self.same_genre_same_plat.pk)

    def test_pads_with_same_genre_if_needed(self):
        results = _get_db_similar_games(self.juego)
        ids = [g['id'] for g in results]
        self.assertIn(self.same_genre_diff_plat.pk, ids)

    def test_excludes_different_genre(self):
        results = _get_db_similar_games(self.juego)
        ids = [g['id'] for g in results]
        self.assertNotIn(self.diff_genre.pk, ids)

    def test_result_includes_required_fields(self):
        results = _get_db_similar_games(self.juego)
        self.assertTrue(len(results) > 0)
        first = results[0]
        for field in ('id', 'name', 'cover_url', 'platform', 'genre'):
            self.assertIn(field, first)

    def test_respects_limit(self):
        for i in range(10):
            Juego.objects.create(Name=f'Platformer {i}', Platform='NES',
                                  Genre='Platform', Rank=100 + i)
        results = _get_db_similar_games(self.juego, limit=4)
        self.assertLessEqual(len(results), 4)
