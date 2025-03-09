"""This module implements a handler for the Python language.

It collects data with [`pytkdocs`](https://github.com/pawamoy/pytkdocs).
"""

import json
import os
import posixpath
import sys
import traceback
from collections.abc import Iterator, Mapping, MutableMapping
from copy import deepcopy
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Any, BinaryIO, ClassVar, Optional

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectionError, CollectorItem, Inventory, get_logger

from mkdocstrings_handlers.python.rendering import (
    do_brief_xref,
    rebuild_category_lists,
    sort_key_alphabetical,
    sort_key_source,
    sort_object,
)

# TODO: add a deprecation warning once the new handler handles 95% of use-cases

logger = get_logger(__name__)


class PythonHandler(BaseHandler):
    """The Python handler class."""

    name: ClassVar[str] = "python"
    """The handler name."""
    domain: ClassVar[str] = "py"  # to match Sphinx's default domain
    """The domain of the handler."""
    enable_inventory: ClassVar[bool] = True
    """Whether the handler supports inventory files."""

    fallback_theme: ClassVar[str] = "material"
    """The fallback theme to use when the user-selected theme is not supported."""
    fallback_config: ClassVar[dict] = {"docstring_style": "markdown", "filters": ["!.*"]}
    """The configuration used when falling back to re-collecting an object to get its anchor.

    This configuration is used in [`Handlers.get_anchors`][mkdocstrings.Handlers.get_anchors].

    When trying to fix (optional) cross-references, the autorefs plugin will try to collect
    an object with every configured handler until one succeeds. It will then try to get
    an anchor for it. It's because objects can have multiple identifiers (aliases),
    for example their definition path and multiple import paths in Python.

    When re-collecting the object, we have no use for its members, or for its docstring being parsed.
    This is why the fallback configuration filters every member out, and uses the Markdown style,
    which we know will not generate any warnings.
    """

    default_config: ClassVar[dict] = {
        "filters": ["!^_[^_]"],
        "show_root_heading": False,
        "show_root_toc_entry": True,
        "show_root_full_path": True,
        "show_root_members_full_path": False,
        "show_object_full_path": False,
        "show_category_heading": False,
        "show_if_no_docstring": False,
        "show_signature": True,
        "show_signature_annotations": False,
        "show_source": True,
        "show_bases": True,
        "group_by_category": True,
        "heading_level": 2,
        "members_order": "alphabetical",
    }
    """
    **Headings options:**

    - `heading_level` (`int`): The initial heading level to use. Default: `2`.
    - `show_root_heading` (`bool`): Show the heading of the object at the root of the documentation tree
        (i.e. the object referenced by the identifier after `:::`). Default: `False`.
    - `show_root_toc_entry` (`bool`): If the root heading is not shown, at least add a ToC entry for it. Default: `True`.
    - `show_root_full_path` (`bool`): Show the full Python path for the root object heading. Default: `True`.
    - `show_root_members_full_path` (`bool`): Show the full Python path of the root members. Default: `False`.
    - `show_object_full_path` (`bool`): Show the full Python path of every object. Default: `False`.
    - `show_category_heading` (`bool`): When grouped by categories, show a heading for each category. Default: `False`.

    **Members options:**

    - `members` (`list[str] | False | None`): An explicit list of members to render. Default: `None`.
    - `members_order` (`str`): The members ordering to use. Options: `alphabetical` - order by the members names,
        `source` - order members as they appear in the source file. Default: `"alphabetical"`.
    - `filters` (`list[str] | None`): A list of filters applied to filter objects based on their name.
        A filter starting with `!` will exclude matching objects instead of including them.
        The `members` option takes precedence over `filters` (filters will still be applied recursively
        to lower members in the hierarchy). Default: `["!^_[^_]"]`.
    - `group_by_category` (`bool`): Group the object's children by categories: attributes, classes, functions, and modules. Default: `True`.

    **Docstrings options:**

    - `docstring_style` (`str`): The docstring style to use: `google`, `numpy`, `restructured-text`, or `None`. Default: `"google"`.
    - `docstring_options` (`dict`): The options for the docstring parser. See parsers under [`pytkdocs.parsers.docstrings`][].
    - `show_if_no_docstring` (`bool`): Show the object heading even if it has no docstring or children with docstrings. Default: `False`.

    **Signatures/annotations options:**

    - `show_signature` (`bool`): Show methods and functions signatures. Default: `True`.
    - `show_signature_annotations` (`bool`): Show the type annotations in methods and functions signatures. Default: `False`.

    **Additional options:**

    - `show_bases` (`bool`): Show the base classes of a class. Default: `True`.
    - `show_source` (`bool`): Show the source code of this object. Default: `True`.
    """

    def __init__(self, config: dict[str, Any], base_dir: Path, **kwargs: Any) -> None:
        """Initialize the handler.

        When instantiating a Python handler, we open a `pytkdocs` subprocess in the background with `subprocess.Popen`.
        It will allow us to feed input to and read output from this subprocess, keeping it alive during
        the whole documentation generation. Spawning a new Python subprocess for each "autodoc" instruction would be
        too resource intensive, and would slow down `mkdocstrings` a lot.

        Parameters:
            config: The handler configuration.
            base_dir: The base directory of the project.
            **kwargs: Arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.base_dir = base_dir
        self.config = config
        self.global_options = config.get("options", {})

        logger.debug("Opening 'pytkdocs' subprocess")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        paths = config.get("paths") or []
        if not paths and self.base_dir:
            paths.append(self.base_dir)
        search_paths = []
        for path in paths:
            if not os.path.isabs(path) and self.base_dir:
                path = os.path.abspath(os.path.join(self.base_dir, path))  # noqa: PLW2901
            if path not in search_paths:
                search_paths.append(path)
        self._paths = search_paths

        commands = []

        if search_paths:
            commands.extend([f"sys.path.insert(0, {path!r})" for path in reversed(search_paths)])

        if setup_commands := config.get("setup_commands"):
            # prevent the Python interpreter or the setup commands
            # from writing to stdout as it would break pytkdocs output
            commands.extend(
                [
                    "from io import StringIO",
                    "sys.stdout = StringIO()",  # redirect stdout to memory buffer
                    *setup_commands,
                    "sys.stdout.flush()",
                    "sys.stdout = sys.__stdout__",  # restore stdout
                ],
            )

        if commands:
            final_commands = [
                "import sys",
                *commands,
                "from pytkdocs.cli import main as pytkdocs",
                "pytkdocs(['--line-by-line'])",
            ]
            cmd = [sys.executable, "-c", "; ".join(final_commands)]
        else:
            cmd = [sys.executable, "-m", "pytkdocs", "--line-by-line"]

        self.process = Popen(  # noqa: S603
            cmd,
            universal_newlines=True,
            stdout=PIPE,
            stdin=PIPE,
            bufsize=-1,
            env=env,
        )

    def get_inventory_urls(self) -> list[tuple[str, dict[str, Any]]]:
        """Return the URLs of the inventory files to download."""
        return [
            (inv.pop("url"), inv) if isinstance(inv, dict) else (inv, {})
            for inv in deepcopy(self.config.get("import", []))
        ]

    @classmethod
    def load_inventory(
        cls,
        in_file: BinaryIO,
        url: str,
        base_url: Optional[str] = None,
        **kwargs: Any,  # noqa: ARG003
    ) -> Iterator[tuple[str, str]]:
        """Yield items and their URLs from an inventory file streamed from `in_file`.

        This implements mkdocstrings' `load_inventory` "protocol" (see plugin.py).

        Arguments:
            in_file: The binary file-like object to read the inventory from.
            url: The URL that this file is being streamed from (used to guess `base_url`).
            base_url: The URL that this inventory's sub-paths are relative to.
            **kwargs: Ignore additional arguments passed from the config.

        Yields:
            Tuples of (item identifier, item URL).
        """
        if base_url is None:
            base_url = posixpath.dirname(url)

        for item in Inventory.parse_sphinx(in_file, domain_filter=("py",)).values():
            yield item.name, posixpath.join(base_url, item.uri)

    def get_options(self, local_options: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """Return the options to use to collect an object.

        We merge the global options with the options specific to the object being collected.

        Arguments:
            local_options: The selection options.

        Returns:
            The options to use to collect an object.
        """
        return {**self.default_config, **self.global_options, **local_options}

    def collect(self, identifier: str, options: MutableMapping[str, Any]) -> CollectorItem:
        """Collect the documentation tree given an identifier and selection options.

        In this method, we feed one line of JSON to the standard input of the subprocess that was opened
        during instantiation of the collector. Then we read one line of JSON on its standard output.

        We load back the JSON text into a Python dictionary.
        If there is a decoding error, we log it as error and raise a CollectionError.

        If the dictionary contains an `error` key, we log it  as error (with the optional `traceback` value),
        and raise a CollectionError.

        If the dictionary values for keys `loading_errors` and `parsing_errors` are not empty,
        we log them as warnings.

        Then we pick up the only object within the `objects` list (there's always only one, because we collect
        them one by one), rebuild it's categories lists
        (see [`rebuild_category_lists()`][mkdocstrings_handlers.python.rendering.rebuild_category_lists]),
        and return it.

        Arguments:
            identifier: The dotted-path of a Python object available in the Python path.
            options: Selection options, used to alter the data collection done by `pytkdocs`.

        Raises:
            CollectionError: When there was a problem collecting the object documentation.

        Returns:
            The collected object-tree.
        """
        pytkdocs_options = {}
        for option in ("filters", "members", "docstring_style", "docstring_options"):
            if option in options:
                pytkdocs_options[option] = options[option]

        logger.debug("Preparing input")
        json_input = json.dumps({"objects": [{"path": identifier, **pytkdocs_options}]})

        logger.debug("Writing to process' stdin")
        self.process.stdin.write(json_input + "\n")  # type: ignore[union-attr]
        self.process.stdin.flush()  # type: ignore[union-attr]

        logger.debug("Reading process' stdout")
        stdout = self.process.stdout.readline()  # type: ignore[union-attr]

        logger.debug("Loading JSON output as Python object")
        try:
            result = json.loads(stdout)
        except json.decoder.JSONDecodeError as exception:
            error = "\n".join(("Error while loading JSON:", stdout, traceback.format_exc()))
            raise CollectionError(error) from exception

        if "error" in result:
            error = result["error"]
            if "traceback" in result:
                error += f"\n{result['traceback']}"
            raise CollectionError(error)

        for loading_error in result["loading_errors"]:
            logger.warning(loading_error)

        for errors in result["parsing_errors"].values():
            for parsing_error in errors:
                logger.warning(parsing_error)

        # We always collect only one object at a time
        result = result["objects"][0]

        logger.debug("Rebuilding categories and children lists")
        rebuild_category_lists(result)

        return result

    def teardown(self) -> None:
        """Terminate the opened subprocess, set it to `None`."""
        logger.debug("Tearing process down")
        self.process.terminate()

    def render(self, data: CollectorItem, options: MutableMapping[str, Any]) -> str:
        """Render the collected data into HTML."""
        template = self.env.get_template(f"{data['category']}.html")

        # Heading level is a "state" variable, that will change at each step
        # of the rendering recursion. Therefore, it's easier to use it as a plain value
        # than as an item in a dictionary.
        heading_level = options["heading_level"]

        members_order = options["members_order"]
        if members_order == "alphabetical":
            sort_function = sort_key_alphabetical
        elif members_order == "source":
            sort_function = sort_key_source
        else:
            raise PluginError(f"Unknown members_order '{members_order}', choose between 'alphabetical' and 'source'.")

        sort_object(data, sort_function=sort_function)

        return template.render(
            **{"config": options, data["category"]: data, "heading_level": heading_level, "root": True},
        )

    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Return the aliases of an identifier."""
        try:
            data = self.collect(identifier, self.fallback_config)
            return (data["path"],)
        except (CollectionError, KeyError):
            return ()

    def update_env(self, config: dict) -> None:  # noqa: ARG002,D102
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["brief_xref"] = do_brief_xref


def get_handler(
    handler_config: MutableMapping[str, Any],
    tool_config: MkDocsConfig,
    **kwargs: Any,
) -> PythonHandler:
    """Simply return an instance of `PythonHandler`.

    Arguments:
        handler_config: The handler configuration.
        tool_config: The tool (SSG) configuration.

    Returns:
        An instance of `PythonHandler`.
    """
    base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
    return PythonHandler(config=dict(handler_config), base_dir=base_dir, **kwargs)
