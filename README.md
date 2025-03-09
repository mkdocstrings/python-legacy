<h1 align="center">mkdocstrings-python-legacy</h1>

<p align="center">The legacy Python handler for <a href="https://github.com/mkdocstrings/mkdocstrings"><i>mkdocstrings</i></a>.</p>

<p align="center">
  <a href="https://github.com/mkdocstrings/python-legacy/actions?query=workflow%3Aci">
    <img alt="ci" src="https://github.com/mkdocstrings/python-legacy/workflows/ci/badge.svg" />
  </a>
  <a href="https://mkdocstrings.github.io/python-legacy/">
    <img alt="documentation" src="https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat" />
  </a>
  <a href="https://pypi.org/project/mkdocstrings-python-legacy/">
    <img alt="pypi version" src="https://img.shields.io/pypi/v/mkdocstrings-python-legacy.svg" />
  </a>
  <a href="https://gitpod.io/#https://github.com/mkdocstrings/python-legacy">
    <img alt="gitpod" src="https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat" />
  </a>
  <a href="https://gitter.im/mkdocstrings/python-legacy">
    <img alt="gitter" src="https://badges.gitter.im/join%20chat.svg" />
  </a>
</p>

---

<p align="center"><img src="logo.png"></p>

WARNING: We suggest using the new handler instead:
[mkdocstrings-python](https://mkdocstrings.github.io/python/).

## Installation

You can install this handler as a *mkdocstrings* extra:

```toml title="pyproject.toml"
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python-legacy]>=0.18",
]
```

You can also explicitely depend on the handler:

```toml title="pyproject.toml"
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings-python-legacy",
]
```

## Preview

<!-- TODO: update the GIF with a more recent screen capture. Maybe use mp4 instead -->
![mkdocstrings_python_gif](https://user-images.githubusercontent.com/3999221/77157838-7184db80-6aa2-11ea-9f9a-fe77405202de.gif)

## Features

- **Data collection from source code**: collection of the object-tree and the docstrings is done thanks to
  [pytkdocs](https://github.com/mkdocstrings/pytkdocs).

- **Support for type annotations:** pytkdocs collects your type annotations and *mkdocstrings* uses them
  to display parameters types or return types.

- **Recursive documentation of Python objects:** just use the module dotted-path as identifier, and you get the full
  module docs. You don't need to inject documentation for each class, function, etc.

- **Support for documented attributes:** attributes (variables) followed by a docstring (triple-quoted string) will
  be recognized by Griffe in modules, classes and even in `__init__` methods.

- **Multiple docstring-styles support:** common support for Google-style, Numpydoc-style,
  and Sphinx-style docstrings.

- **Admonition support in Google docstrings:** blocks like `Note:` or `Warning:` will be transformed
  to their [admonition](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) equivalent.
  *We do not support nested admonitions in docstrings!*

- **Every object has a TOC entry:** we render a heading for each object, meaning *MkDocs* picks them into the Table
  of Contents, which is nicely display by the Material theme. Thanks to *mkdocstrings* cross-reference ability,
  you can reference other objects within your docstrings, with the classic Markdown syntax:
  `[this object][package.module.object]` or directly with `[package.module.object][]`

- **Source code display:** *mkdocstrings* can add a collapsible div containing the highlighted source code
  of the Python object.
