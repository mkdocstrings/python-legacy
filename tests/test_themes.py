"""Tests for the different themes we claim to support."""

import sys

import pytest


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
def test_render_themes_templates(module, plugin):
    """Test rendering of a given theme's templates.

    Parameters:
        module: The module to load and render (parametrized).
        plugin: The plugin instance (parametrized fixture).
    """
    handler = plugin.handlers.get_handler("python")
    handler._update_env(plugin.md, plugin.handlers._config)  # noqa: WPS437
    data = handler.collect(module, {})
    handler.render(data, {})
