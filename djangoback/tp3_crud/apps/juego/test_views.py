import json
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Juego

User = get_user_model()

_ENRICHED_PATH   = 'apps.juego.views.api.get_enriched_game'
_CHAT_REPLY_PATH = 'apps.juego.views.api.get_chat_reply'


class ApiJuegosViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='tester', password='pass')
        for i in range(5):
            Juego.objects.create(Name=f'NES Game {i}', Platform='NES',
                                  Year=1985, Genre='Platform', Rank=i + 1)

    def test_unauthenticated_redirects(self):
        response = self.client.get('/api/juegos/')
        self.assertEqual(response.status_code, 302)

    def test_no_filters_returns_shelves_mode(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/juegos/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['mode'], 'shelves')

    def test_query_returns_search_mode(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/juegos/?q=NES')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['mode'], 'search')
        self.assertEqual(data['total'], 5)

    def test_platform_filter_returns_search_mode(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/juegos/?platform=NES')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['mode'], 'search')

    def test_year_filter_returns_search_mode(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/juegos/?year_from=1985&year_to=1985')
        data = response.json()
        self.assertEqual(data['mode'], 'search')
        self.assertEqual(data['total'], 5)

    def test_search_no_results(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/juegos/?q=zzznomatch')
        self.assertEqual(response.json()['total'], 0)


class ApiIgdbFichaViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='tester', password='pass')
        cls.juego = Juego.objects.create(Name='Mario', Platform='NES', Year=1985, Genre='Platform')

    def test_unauthenticated_redirects(self):
        response = self.client.get(f'/api/igdb-ficha/?game_id={self.juego.pk}')
        self.assertEqual(response.status_code, 302)

    def test_missing_game_id_returns_400(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/igdb-ficha/')
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_game_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/igdb-ficha/?game_id=99999')
        self.assertEqual(response.status_code, 404)

    @patch(_ENRICHED_PATH, return_value={'name': 'Mario', 'summary': 'Un juego de plataformas'})
    def test_returns_enriched_data(self, _mock):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/igdb-ficha/?game_id={self.juego.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Mario')

    @patch(_ENRICHED_PATH, return_value=None)
    def test_service_returning_none_gives_404(self, _mock):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/igdb-ficha/?game_id={self.juego.pk}')
        self.assertEqual(response.status_code, 404)


class ApiChatBotViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='tester', password='pass')

    def _post(self, message):
        self.client.force_login(self.user)
        return self.client.post(
            '/api/chat/',
            data=json.dumps({'message': message}),
            content_type='application/json',
        )

    def test_unauthenticated_redirects(self):
        response = self.client.post('/api/chat/', data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_get_method_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/chat/')
        self.assertEqual(response.status_code, 405)

    def test_empty_message_returns_400(self):
        response = self._post('')
        self.assertEqual(response.status_code, 400)
        self.assertIn('vacío', response.json()['reply'])

    @patch(_CHAT_REPLY_PATH, side_effect=ValueError('missing_api_key'))
    def test_missing_api_key_returns_500(self, _mock):
        response = self._post('Hola')
        self.assertEqual(response.status_code, 500)

    @patch(_CHAT_REPLY_PATH, return_value='¡Hola! Soy GameBase.')
    def test_valid_message_returns_reply(self, _mock):
        response = self._post('Hola')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['reply'], '¡Hola! Soy GameBase.')
