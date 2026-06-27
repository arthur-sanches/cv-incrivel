from unittest.mock import MagicMock, patch

from django.test import TestCase

from ai_integration.services import OpenRouterClient, OpenRouterIntegrationError


class OpenRouterClientUnitTest(TestCase):
    """Unit tests for :class:`OpenRouterClient`.

    These tests mock the OpenRouter SDK so they run offline and do not
    require a valid API key.
    """

    def _build_choice(self, content="OK"):
        """Build a fake chat choice with the given content."""
        message = MagicMock()
        message.content = content
        choice = MagicMock()
        choice.message = message
        return choice

    def _build_result(self, choices):
        """Build a fake ChatResult with the given choices."""
        result = MagicMock()
        result.choices = choices
        return result

    def test_init_requires_non_empty_command(self):
        with self.assertRaises(ValueError):
            OpenRouterClient(command="", data="anything")

    def test_attributes_are_set_on_init(self):
        client = OpenRouterClient(
            command="This is a simple test.",
            data="Just answer with 'OK'",
        )

        self.assertEqual(client.command, "This is a simple test.")
        self.assertEqual(client.data, "Just answer with 'OK'")
        self.assertEqual(client.response, "")

    def test_build_messages_contains_command_and_data(self):
        client = OpenRouterClient(
            command="This is a simple test.",
            data="Just answer with 'OK'",
        )

        messages = client._build_messages()

        self.assertEqual(len(messages), 2)
        # System message
        self.assertEqual(messages[0].role, "system")
        # User message contains both command and data
        user_content = messages[1].content
        self.assertIn("This is a simple test.", user_content)
        self.assertIn("Just answer with 'OK'", user_content)
        self.assertEqual(messages[1].role, "user")

    @patch("ai_integration.services.OpenRouter")
    def test_run_returns_response_string(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        mock_client.chat.send.return_value = self._build_result(
            [self._build_choice(content="OK")]
        )

        client = OpenRouterClient(
            command="This is a simple test.",
            data="Just answer with 'OK'",
        )
        response = client.run()

        self.assertEqual(response, "OK")
        self.assertEqual(client.response, "OK")
        mock_client.chat.send.assert_called_once()

    @patch("ai_integration.services.OpenRouter")
    def test_run_normalises_list_content_to_string(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        # Simulate a response where content is a list of content items.
        item1 = MagicMock()
        item1.text = "Hello "
        item2 = MagicMock()
        item2.text = "World"
        mock_client.chat.send.return_value = self._build_result(
            [self._build_choice(content=[item1, item2])]
        )

        client = OpenRouterClient(command="test", data="data")
        response = client.run()

        self.assertEqual(response, "Hello World")

    @patch("ai_integration.services.OpenRouter")
    def test_run_raises_error_on_sdk_exception(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        mock_client.chat.send.side_effect = RuntimeError("network error")

        client = OpenRouterClient(command="test", data="data")

        with self.assertRaises(OpenRouterIntegrationError):
            client.run()

    @patch("ai_integration.services.OpenRouter")
    def test_run_raises_error_on_empty_choices(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        mock_client.chat.send.return_value = self._build_result([])

        client = OpenRouterClient(command="test", data="data")

        with self.assertRaises(OpenRouterIntegrationError):
            client.run()

    @patch("ai_integration.services.OpenRouter")
    def test_run_raises_error_when_content_is_none(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        mock_client.chat.send.return_value = self._build_result(
            [self._build_choice(content=None)]
        )

        client = OpenRouterClient(command="test", data="data")

        with self.assertRaises(OpenRouterIntegrationError):
            client.run()

    @patch("ai_integration.services.OpenRouter")
    def test_run_uses_custom_system_prompt(self, mock_openrouter_cls):
        mock_client = MagicMock()
        mock_openrouter_cls.return_value = mock_client
        mock_client.chat.send.return_value = self._build_result(
            [self._build_choice(content="OK")]
        )

        client = OpenRouterClient(
            command="test",
            data="data",
            system_prompt="You are a strict validator.",
        )
        client.run()

        sent_messages = mock_client.chat.send.call_args.kwargs["messages"]
        self.assertEqual(sent_messages[0].content, "You are a strict validator.")


class OpenRouterClientIntegrationTest(TestCase):
    """Integration test for the :class:`OpenRouterClient`.

    This test performs a real request against the OpenRouter API and therefore
    requires a valid API key configured either in ``settings.OPENROUTER_API_KEY``
    or in the ``OPENROUTER_API_KEY`` environment variable.
    """

    def test_run_returns_ok_response(self):
        client = OpenRouterClient(
            command="This is a simple test.",
            data="Just answer with 'OK'",
        )

        response = client.run()

        self.assertEqual(response.strip().upper(), "OK")
        self.assertEqual(client.response.strip().upper(), "OK")
