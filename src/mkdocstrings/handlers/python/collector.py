"""This module implements a collector for the Python language.

It collects data with [`pytkdocs`](https://github.com/pawamoy/pytkdocs).
"""

import json
import os
import sys
import traceback
from collections import ChainMap
from subprocess import PIPE, Popen  # noqa: S404 (what other option, more secure that PIPE do we have? sockets?)
from typing import List, Optional

from mkdocstrings.handlers.base import BaseCollector, CollectionError, CollectorItem
from mkdocstrings.loggers import get_logger

log = get_logger(__name__)


class PythonCollector(BaseCollector):
    """The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.base.BaseRenderer].
    """

    default_config: dict = {"filters": ["!^_[^_]"]}
    """The default selection options.

    Option | Type | Description | Default
    ------ | ---- | ----------- | -------
    **`filters`** | `List[str]` | Filter members with regular expressions. | `[ "!^_[^_]" ]`
    **`members`** | `Union[bool, List[str]]` | Explicitly select the object members. | *`pytkdocs` default: `True`*

    If `members` is a list of names, filters are applied only on the members children (not the members themselves).
    If `members` is `False`, none are selected.
    If `members` is `True` or an empty list, filters are applied on all members and their children.

    Members affect only the first layer of objects, while filters affect the whole object-tree recursively.

    Every filters is run against every object name. An object can be un-selected by a filter and re-selected by the
    next one:

    - `"!^_"`: exclude all objects starting with an underscore
    - `"^__"`: but select all objects starting with **two** underscores

    Obviously one could use a single filter instead: `"!^_[^_]"`, which is the default.
    """

    fallback_config = {"docstring_style": "markdown", "filters": ["!.*"]}
    """The configuration used when falling back to re-collecting an object to get its anchor.

    This configuration is used in [`Handlers.get_anchors`][mkdocstrings.handlers.base.Handlers.get_anchors].

    When trying to fix (optional) cross-references, the autorefs plugin will try to collect
    an object with every configured handler until one succeeds. It will then try to get
    an anchor for it. It's because objects can have multiple identifiers (aliases),
    for example their definition path and multiple import paths in Python.

    When re-collecting the object, we have no use for its members, or for its docstring being parsed.
    This is why the fallback configuration filters every member out, and uses the Markdown style,
    which we know will not generate any warnings.
    """

    def __init__(self, setup_commands: Optional[List[str]] = None) -> None:
        """Initialize the object.

        When instantiating a Python collector, we open a subprocess in the background with `subprocess.Popen`.
        It will allow us to feed input to and read output from this subprocess, keeping it alive during
        the whole documentation generation. Spawning a new Python subprocess for each "autodoc" instruction would be
        too resource intensive, and would slow down `mkdocstrings` a lot.

        Arguments:
            setup_commands: A list of python commands as strings to be executed in the subprocess before `pytkdocs`.
        """
        log.debug("Opening 'pytkdocs' subprocess")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        if setup_commands:
            # prevent the Python interpreter or the setup commands
            # from writing to stdout as it would break pytkdocs output
            commands = [
                "import sys",
                "from io import StringIO",
                "from pytkdocs.cli import main as pytkdocs",
                "sys.stdout = StringIO()",  # redirect stdout to memory buffer
                *setup_commands,
                "sys.stdout.flush()",
                "sys.stdout = sys.__stdout__",  # restore stdout
                "pytkdocs(['--line-by-line'])",
            ]
            cmd = [sys.executable, "-c", "; ".join(commands)]
        else:
            cmd = [sys.executable, "-m", "pytkdocs", "--line-by-line"]

        self.process = Popen(  # noqa: S603,S607 (we trust the input, and we don't want to use the absolute path)
            cmd,
            universal_newlines=True,
            stdout=PIPE,
            stdin=PIPE,
            bufsize=-1,
            env=env,
        )

    def collect(self, identifier: str, config: dict) -> CollectorItem:
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
        (see [`rebuild_category_lists()`][mkdocstrings.handlers.python.rebuild_category_lists]),
        and return it.

        Arguments:
            identifier: The dotted-path of a Python object available in the Python path.
            config: Selection options, used to alter the data collection done by `pytkdocs`.

        Raises:
            CollectionError: When there was a problem collecting the object documentation.

        Returns:
            The collected object-tree.
        """
        final_config = ChainMap(config, self.default_config)

        log.debug("Preparing input")
        json_input = json.dumps({"objects": [{"path": identifier, **final_config}]})

        log.debug("Writing to process' stdin")
        self.process.stdin.write(json_input + "\n")  # type: ignore
        self.process.stdin.flush()  # type: ignore

        log.debug("Reading process' stdout")
        stdout = self.process.stdout.readline()  # type: ignore

        log.debug("Loading JSON output as Python object")
        try:
            result = json.loads(stdout)
        except json.decoder.JSONDecodeError as exception:
            error = "\n".join(("Error while loading JSON:", stdout, traceback.format_exc()))
            raise CollectionError(error) from exception

        error = result.get("error")
        if error:
            if "traceback" in result:
                error += f"\n{result['traceback']}"
            raise CollectionError(error)

        for loading_error in result["loading_errors"]:
            log.warning(loading_error)

        for errors in result["parsing_errors"].values():
            for parsing_error in errors:
                log.warning(parsing_error)

        # We always collect only one object at a time
        result = result["objects"][0]

        log.debug("Rebuilding categories and children lists")
        rebuild_category_lists(result)

        return result

    def teardown(self) -> None:
        """Terminate the opened subprocess, set it to `None`."""
        log.debug("Tearing process down")
        self.process.terminate()


def rebuild_category_lists(obj: dict) -> None:
    """Recursively rebuild the category lists of a collected object.

    Since `pytkdocs` dumps JSON on standard output, it must serialize the object-tree and flatten it to reduce data
    duplication and avoid cycle-references. Indeed, each node of the object-tree has a `children` list, containing
    all children, and another list for each category of children: `attributes`, `classes`, `functions`, `methods`
    and `modules`. It replaces the values in category lists with only the paths of the objects.

    Here, we reconstruct these category lists by picking objects in the `children` list using their path.

    For each object, we recurse on every one of its children.

    Arguments:
        obj: The collected object, loaded back from JSON into a Python dictionary.
    """
    for category in ("attributes", "classes", "functions", "methods", "modules"):
        obj[category] = [obj["children"][path] for path in obj[category]]
    obj["children"] = [child for _, child in obj["children"].items()]
    for child in obj["children"]:
        rebuild_category_lists(child)
