"""OpenRouter integration service.

This module provides an agnostic wrapper around the OpenRouter Client SDK.
The :class:`OpenRouterClient` exposes a simple ``command`` / ``data`` interface
that returns a single ``response`` string, keeping callers decoupled from the
underlying SDK details.
"""

from __future__ import annotations

import os
from typing import Optional

from django.conf import settings

from openrouter import OpenRouter
from openrouter import components


class OpenRouterIntegrationError(Exception):
    """Raised when a request to OpenRouter fails."""


class OpenRouterClient:
    """Agnostic OpenRouter integration.

    The integration is agnostic regarding the intent of the request: callers
    only need to provide a ``command`` describing what they want the model to
    do and the ``data`` the command should operate on. The class builds the
    appropriate chat messages, calls the OpenRouter SDK and returns the
    resulting text as ``response``.

    Attributes:
        command: A string describing the action/instruction to perform.
        data: A string with the input data the command should operate on.
        response: A string with the model's textual response (available after
            :meth:`run` is called).
    """

    # Default model used when none is provided. Can be overridden per call
    # or through the ``OPENROUTER_MODEL`` environment variable.
    DEFAULT_MODEL = "openrouter/auto"

    def __init__(
        self,
        command: str,
        data: Optional[str] = "",
        system_prompt: Optional[str] = None,
        *,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        http_referer: Optional[str] = None,
        app_title: Optional[str] = None,
    ) -> None:
        if not command:
            raise ValueError("'command' must be a non-empty string.")

        self.command: str = command
        self.data: str = data
        self.response: str = ""
        self._system_prompt: Optional[str] = system_prompt

        self._model = (
            model
            or os.getenv("OPENROUTER_MODEL")
            or getattr(settings, "OPENROUTER_MODEL", self.DEFAULT_MODEL)
        )
        self._api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or getattr(settings, "OPENROUTER_API_KEY", "")
            or None
        )
        self._http_referer = (
            http_referer
            or os.getenv("OPENROUTER_HTTP_REFERER")
            or getattr(settings, "OPENROUTER_HTTP_REFERER", "")
            or None
        )
        self._app_title = (
            app_title
            or os.getenv("OPENROUTER_X_OPEN_ROUTER_TITLE")
            or getattr(settings, "OPENROUTER_X_OPEN_ROUTER_TITLE", "")
            or None
        )

        self._client = OpenRouter(
            api_key=self._api_key,
            http_referer=self._http_referer,
            x_open_router_title=self._app_title,
        )

    def _build_messages(self) -> list:
        """Build the chat messages from ``command`` and ``data``."""
        system_content = (
            self._system_prompt
            or "You are an AI assistant that executes commands on provided data."
        )
        user_content = (
            f"Command:\n{self.command}\n\n"
            f"Data:\n{self.data}\n\n"
            "Respond with the result of applying the command to the data."
        )
        return [
            components.ChatSystemMessage(content=system_content, role="system"),
            components.ChatUserMessage(content=user_content, role="user"),
        ]

    def run(self) -> str:
        """Execute the request against OpenRouter and populate ``response``.

        Returns:
            The textual response produced by the model.
        """
        try:
            result = self._client.chat.send(
                model=self._model,
                messages=self._build_messages(),
            )
        except Exception as exc:  # pragma: no cover - depends on network
            raise OpenRouterIntegrationError(
                f"OpenRouter request failed: {exc}"
            ) from exc

        if not result or not getattr(result, "choices", None):
            raise OpenRouterIntegrationError(
                "OpenRouter returned an empty response."
            )

        choice = result.choices[0]
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None) if message else None

        if content is None:
            raise OpenRouterIntegrationError(
                "OpenRouter response did not contain any content."
            )

        # ``content`` may be a string or a list of content items; normalise
        # to a plain string for the agnostic interface.
        if isinstance(content, list):
            content = "".join(
                str(getattr(item, "text", item)) for item in content
            )

        self.response = str(content)
        return self.response
