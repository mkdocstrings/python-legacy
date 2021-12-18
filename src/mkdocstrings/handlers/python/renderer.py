"""This module implements a renderer for the Python language."""

import sys
from collections import ChainMap
from typing import Any, Callable, Sequence

from markdown import Markdown
from markupsafe import Markup

from mkdocstrings.extension import PluginError
from mkdocstrings.handlers.base import BaseRenderer, CollectorItem
from mkdocstrings.loggers import get_logger

log = get_logger(__name__)


class PythonRenderer(BaseRenderer):
    """The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.base.BaseRenderer].

    Attributes:
        fallback_theme: The theme to fallback to.
        default_config: The default rendering options,
            see [`default_config`][mkdocstrings.handlers.python.PythonRenderer.default_config].
    """

    fallback_theme = "material"

    default_config: dict = {
        "show_root_heading": False,
        "show_root_toc_entry": True,
        "show_root_full_path": True,
        "show_root_members_full_path": False,
        "show_object_full_path": False,
        "show_category_heading": False,
        "show_if_no_docstring": False,
        "show_signature_annotations": False,
        "show_source": True,
        "show_bases": True,
        "group_by_category": True,
        "heading_level": 2,
        "members_order": "alphabetical",
    }
    """The default rendering options.

    Option | Type | Description | Default
    ------ | ---- | ----------- | -------
    **`show_root_heading`** | `bool` | Show the heading of the object at the root of the documentation tree. | `False`
    **`show_root_toc_entry`** | `bool` | If the root heading is not shown, at least add a ToC entry for it. | `True`
    **`show_root_full_path`** | `bool` | Show the full Python path for the root object heading. | `True`
    **`show_object_full_path`** | `bool` | Show the full Python path of every object. | `False`
    **`show_root_members_full_path`** | `bool` | Show the full Python path of objects that are children of the root object (for example, classes in a module). When False, `show_object_full_path` overrides. | `False`
    **`show_category_heading`** | `bool` | When grouped by categories, show a heading for each category. | `False`
    **`show_if_no_docstring`** | `bool` | Show the object heading even if it has no docstring or children with docstrings. | `False`
    **`show_signature_annotations`** | `bool` | Show the type annotations in methods and functions signatures. | `False`
    **`show_source`** | `bool` | Show the source code of this object. | `True`
    **`show_bases`** | `bool` | Show the base classes of a class. | `True`
    **`group_by_category`** | `bool` | Group the object's children by categories: attributes, classes, functions, methods, and modules. | `True`
    **`heading_level`** | `int` | The initial heading level to use. | `2`
    **`members_order`** | `str` | The members ordering to use. Options: `alphabetical` - order by the members names, `source` - order members as they appear in the source file. | `alphabetical`
    """  # noqa: E501

    def render(self, data: CollectorItem, config: dict) -> str:  # noqa: D102 (ignore missing docstring)
        final_config = ChainMap(config, self.default_config)

        template = self.env.get_template(f"{data['category']}.html")

        # Heading level is a "state" variable, that will change at each step
        # of the rendering recursion. Therefore, it's easier to use it as a plain value
        # than as an item in a dictionary.
        heading_level = final_config["heading_level"]
        members_order = final_config["members_order"]

        if members_order == "alphabetical":
            sort_function = _sort_key_alphabetical
        elif members_order == "source":
            sort_function = _sort_key_source
        else:
            raise PluginError(f"Unknown members_order '{members_order}', choose between 'alphabetical' and 'source'.")

        sort_object(data, sort_function=sort_function)

        return template.render(
            **{"config": final_config, data["category"]: data, "heading_level": heading_level, "root": True},
        )

    def get_anchors(self, data: CollectorItem) -> Sequence[str]:  # noqa: D102 (ignore missing docstring)
        try:
            return (data["path"],)
        except KeyError:
            return ()

    def update_env(self, md: Markdown, config: dict) -> None:  # noqa: D102 (ignore missing docstring)
        super().update_env(md, config)
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["brief_xref"] = self.do_brief_xref

    def do_brief_xref(self, path: str) -> Markup:
        """Filter to create cross-reference with brief text and full identifier as hover text.

        Arguments:
            path: The path to shorten and render.

        Returns:
            A span containing the brief cross-reference and the full one on hover.
        """
        brief = path.split(".")[-1]
        return Markup("<span data-autorefs-optional-hover={path}>{brief}</span>").format(path=path, brief=brief)


def sort_object(obj: CollectorItem, sort_function: Callable[[CollectorItem], Any]) -> None:
    """Sort the collected object's children.

    Sorts the object's children list, then each category separately, and then recurses into each.

    Arguments:
        obj: The collected object, as a dict. Note that this argument is mutated.
        sort_function: The sort key function used to determine the order of elements.
    """
    obj["children"].sort(key=sort_function)

    for category in ("attributes", "classes", "functions", "methods", "modules"):
        obj[category].sort(key=sort_function)

    for child in obj["children"]:
        sort_object(child, sort_function=sort_function)


def _sort_key_alphabetical(item: CollectorItem) -> Any:
    # chr(sys.maxunicode) is a string that contains the final unicode
    # character, so if 'name' isn't found on the object, the item will go to
    # the end of the list.
    return item.get("name", chr(sys.maxunicode))


def _sort_key_source(item: CollectorItem) -> Any:
    # if 'line_start' isn't found on the object, the item will go to
    # the start of the list.
    return item.get("source", {}).get("line_start", -1)
