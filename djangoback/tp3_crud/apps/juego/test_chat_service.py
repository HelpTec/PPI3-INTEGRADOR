from unittest.mock import patch, MagicMock
from django.test import TestCase
from .services.chat_service import get_chat_reply

_GENAI_PATH = 'apps.juego.services.chat_service.genai'


class GetChatReplyTest(TestCase):
    def test_raises_on_empty_string(self):
        with self.assertRaises(ValueError) as ctx:
            get_chat_reply('')
        self.assertEqual(str(ctx.exception), 'empty_message')

    def test_raises_on_whitespace_only(self):
        with self.assertRaises(ValueError) as ctx:
            get_chat_reply('   ')
        self.assertEqual(str(ctx.exception), 'empty_message')

    @patch.dict('os.environ', {}, clear=True)
    def test_raises_when_api_key_missing(self):
        with self.assertRaises(ValueError) as ctx:
            get_chat_reply('Hola')
        self.assertEqual(str(ctx.exception), 'missing_api_key')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'TU_CLAVE_DE_GEMINI_AQUI'})
    def test_raises_on_placeholder_key(self):
        with self.assertRaises(ValueError) as ctx:
            get_chat_reply('Hola')
        self.assertEqual(str(ctx.exception), 'missing_api_key')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'fake-key'})
    @patch(_GENAI_PATH)
    def test_returns_reply_text(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value.text = '¡Hola! Soy GameBase.'
        result = get_chat_reply('Hola')
        self.assertEqual(result, '¡Hola! Soy GameBase.')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'fake-key'})
    @patch(_GENAI_PATH)
    def test_includes_message_in_prompt(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value.text = 'ok'
        get_chat_reply('¿Cuál es el mejor juego de NES?')
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get('contents') or call_args.args[1]
        self.assertIn('¿Cuál es el mejor juego de NES?', prompt)

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'fake-key'})
    @patch(_GENAI_PATH)
    def test_uses_correct_model(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value.text = 'ok'
        get_chat_reply('test')
        call_args = mock_client.models.generate_content.call_args
        model = call_args.kwargs.get('model') or call_args.args[0]
        self.assertEqual(model, 'gemini-2.5-flash')
