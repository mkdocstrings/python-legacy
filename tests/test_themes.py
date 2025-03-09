"""Tests for the different themes we claim to support."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from mkdocstrings import MkdocstringsPlugin


@pytest.mark.parametrize(
    "plugin",
    [
        {"theme": "mkdocs"},
        {"theme": "readthedocs"},
        {"theme": {"name": "material"}},
    ],
    indirect=["plugin"],
)
@pytest.mark.parametrize(
    "module",
    [
        "mkdocstrings.extension",
        "mkdocstrings.inventory",
        "mkdocstrings.loggers",
        "mkdocstrings.handlers.base",
        "mkdocstrings.handlers.rendering",
        "mkdocstrings_handlers.python.handler",
        "mkdocstrings_handlers.python.rendering",
    ],
)
def test_render_themes_templates(module: str, plugin: MkdocstringsPlugin) -> None:
    """Test rendering of a given theme's templates.

    Parameters:
        module: The module to load and render (parametrized).
        plugin: The plugin instance (parametrized fixture).
    """
    handler = plugin.handlers.get_handler("python")
    handler._update_env(plugin.md, config=plugin.handlers._tool_config)  # type: ignore[attr-defined]
    options = handler.get_options({})
    data = handler.collect(module, options)
    handler.render(data, options)
