# mkdocstrings-python-legacy

The legacy Python handler for [*mkdocstrings*](https://github.com/mkdocstrings/mkdocstrings).

______________________________________________________________________

Warning

We suggest using the new handler instead: [mkdocstrings-python](https://mkdocstrings.github.io/python/).

## Installation

You can install this handler as a *mkdocstrings* extra:

pyproject.toml

```
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python-legacy]>=0.18",
]

```

You can also explicitely depend on the handler:

pyproject.toml

```
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings-python-legacy",
]

```

## Preview

## Features

- **Data collection from source code**: collection of the object-tree and the docstrings is done thanks to [pytkdocs](https://github.com/mkdocstrings/pytkdocs).
- **Support for type annotations:** pytkdocs collects your type annotations and *mkdocstrings* uses them to display parameters types or return types.
- **Recursive documentation of Python objects:** just use the module dotted-path as identifier, and you get the full module docs. You don't need to inject documentation for each class, function, etc.
- **Support for documented attributes:** attributes (variables) followed by a docstring (triple-quoted string) will be recognized by Griffe in modules, classes and even in `__init__` methods.
- **Multiple docstring-styles support:** common support for Google-style, Numpydoc-style, and Sphinx-style docstrings.
- **Admonition support in Google docstrings:** blocks like `Note:` or `Warning:` will be transformed to their [admonition](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) equivalent. *We do not support nested admonitions in docstrings!*
- **Every object has a TOC entry:** we render a heading for each object, meaning *MkDocs* picks them into the Table of Contents, which is nicely display by the Material theme. Thanks to *mkdocstrings* cross-reference ability, you can reference other objects within your docstrings, with the classic Markdown syntax: `[this object][package.module.object]` or directly with `[package.module.object][]`
- **Source code display:** *mkdocstrings* can add a collapsible div containing the highlighted source code of the Python object.
