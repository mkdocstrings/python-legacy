"""Configuration for the pytest test suite."""

from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING

import pytest
from markdown.core import Markdown
from mkdocs.config.defaults import MkDocsConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from mkdocstrings import MkdocstringsExtension, MkdocstringsPlugin


@pytest.fixture(name="mkdocs_conf")
def fixture_mkdocs_conf(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[MkDocsConfig]:
    """Yield a MkDocs configuration object.

    Parameters:
        request: Pytest request fixture.
        tmp_path: Pytest temporary path fixture.

    Yields:
        MkDocs configuration object.
    """
    conf = MkDocsConfig()
    while hasattr(request, "_parent_request") and hasattr(request._parent_request, "_parent_request"):
        request = request._parent_request

    conf_dict = {
        "site_name": "foo",
        "site_url": "https://example.org/",
        "site_dir": str(tmp_path),
        "plugins": [{"mkdocstrings": {"default_handler": "python"}}],
        **getattr(request, "param", {}),
    }
    # Re-create it manually as a workaround for https://github.com/mkdocs/mkdocs/issues/2289
    mdx_configs = dict(ChainMap(*conf_dict.get("markdown_extensions", [])))

    conf.load_dict(conf_dict)
    assert conf.validate() == ([], [])

    conf["mdx_configs"] = mdx_configs
    conf["markdown_extensions"].insert(0, "toc")  # Guaranteed to be added by MkDocs.

    conf = conf["plugins"]["mkdocstrings"].on_config(conf)
    conf = conf["plugins"]["autorefs"].on_config(conf)
    yield conf
    conf["plugins"]["mkdocstrings"].on_post_build(conf)


@pytest.fixture(name="plugin")
def fixture_plugin(mkdocs_conf: MkDocsConfig) -> MkdocstringsPlugin:
    """Return a plugin instance.

    Parameters:
        mkdocs_conf: MkDocs configuration object (fixture).

    Returns:
        Configurated plugin instance.
    """
    plugin = mkdocs_conf["plugins"]["mkdocstrings"]
    plugin.md = Markdown(extensions=mkdocs_conf["markdown_extensions"], extension_configs=mkdocs_conf["mdx_configs"])
    return plugin


@pytest.fixture(name="ext_markdown")
def fixture_ext_markdown(plugin: MkdocstringsPlugin) -> MkdocstringsExtension:
    """Return a Markdown instance with MkdocstringsExtension.

    Parameters:
        plugin: A configurated plugin instance. (fixture).

    Returns:
        The plugin Markdown instance.
    """
    return plugin.md  # type: ignore[attr-defined]
