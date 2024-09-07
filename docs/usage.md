# Usage

WARNING: **This is the documentation for the LEGACY Python handler.**  
To read the documentation for the NEW handler,
go to the [new handler documentation](https://mkdocstrings.github.io/python).

The tool used by the legacy Python handler to collect documentation from Python source code
is [`pytkdocs`](https://mkdocstrings.github.io/pytkdocs).
It stands for *(Python) Take Docs*, and is supposed to be a pun on MkDocs (*Make Docs*?).

Like every handler, the legacy Python handler accepts both **global** and **local** options.

## Global-only options

Some options are **global only**, and go directly under the handler's name.

- `import`: this option is used to import Sphinx-compatible objects inventories from other
    documentation sites. For example, you can import the standard library
    objects inventory like this:

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            import:
            - https://docs.python-requests.org/en/master/objects.inv
    ```

    When importing an inventory, you enable automatic cross-references
    to other documentation sites like the standard library docs
    or any third-party package docs. Typically, you want to import
    the inventories of your project's dependencies, at least those
    that are used in the public API. 

    NOTE: This global option is common to *all* handlers, however
    they might implement it differently (or not even implement it).

- `paths`: this option is used to provide filesystem paths in which to search for Python modules.
    Non-absolute paths are computed as relative to MkDocs configuration file. Example:

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            paths: [src]  # search packages in the src folder
    ```

    More details at [Finding modules](#finding-modules).

  - `setup_commands`: this option is used to instruct `pytkdocs`, the tool responsible
    for collecting data from sources, to run Python statements before starting to collect data.
    It is declared as a list of strings:

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            setup_commands:
            - import os
            - import django
            - os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_app.settings")
            - django.setup()
    ```

    The setup commands are executed only once, when the `pytkdocs` background process is started.

## Global/local options

The other options can be used both globally *and* locally, under the `options` key.
For example, globally:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          do_something: true
```

...and locally, overriding the global configuration:

```md title="docs/some_page.md"
::: package.module.class
    options:
      do_something: false
```

These options affect how the documentation is collected from sources and renderered:
headings, members, docstrings, etc.

### ::: mkdocstrings_handlers.python.handler.PythonHandler.default_config
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Supported docstrings styles

Right now, `pytkdocs` supports the Google-style, Numpy-style and reStructuredText-style docstring formats.
The style used by default is the Google-style.
You can configure what style you want to use with
the `docstring_style` and `docstring_options` options,
both globally or per autodoc instruction.

### Google-style

You can see examples of Google-style docstrings
in [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

#### Sections

Docstrings sections are parsed by `pytkdocs` and rendered by *mkdocstrings*.
Supported sections are:

- `Arguments` (or `Args`, `Parameters`, `Params`)
- `Attributes`
- `Examples` (or `Example`)
- `Raises` (or `Raise`, `Except`, `Exceptions`)
- `Returns` (or `Return`)

#### Admonitions

Additionally, any section that is not recognized will be transformed into its admonition equivalent.
For example:

=== "Original"
    ```python
    """
    Note: You can disable this behavior with the `replace_admonitions` option.
        To prevent `pytkdocs` from converting sections to admonitions,
        use the `replace_admonitions`:
       
        ```md
        ::: my_package.my_module
            options:
              docstring_style: google  # this is the default
              docstring_options:
                replace_admonitions: no 
        ```
        
        So meta!
    """
    ```

=== "Modified"
    ```python
    """
    !!! note "You can disable this behavior with the `replace_admonitions` option."
        To prevent `pytkdocs` from converting sections to admonitions,
        use the `replace_admonitions`:
       
        ```md
        ::: my_package.my_module
            options:
              docstring_style: google  # this is the default
              docstring_options:
                replace_admonitions: no 
        ```
        
        So meta!
    """
    ```
    
=== "Result"
    > NOTE: **You can disable this behavior with the `replace_admonitions` parser option.**  
    > To prevent `pytkdocs` from converting sections to admonitions,
    > use the `replace_admonitions` parser option:
    > 
    > ```md
    > ::: my_package.my_module
    >     options:
    >       docstring_style: google  # this is the default
    >       docstring_options:
    >         replace_admonitions: no 
    > ```
    > 
    > So meta!

As shown in the above example, this can be disabled
with the `replace_admonitions` option of the Google-style parser:

```yaml
::: my_package.my_module
    options:
      docstring_style: google  # this is the default
      docstring_options:
        replace_admonitions: no 
```

#### Annotations

Type annotations are read both in the code and in the docstrings.

> EXAMPLE: **Example with a function**  
> **Expand the source at the end to see the original code!**
>
> ### ::: snippets.function_annotations_google:my_function
>     options:
>       show_root_heading: false
>       show_root_toc_entry: false

### Numpy-style

IMPORTANT: **Extra dependency required**  
You'll need an extra dependency to parse Numpy-style docstrings:
```
pdm add -d --group docs 'pytkdocs[numpy-style]'
poetry add -D 'pytkdocs[numpy-style]'
pip install 'pytkdocs[numpy-style]'
# etc.
```

NOTE: As Numpy-style is partially supported by the underlying parser,
you may experience problems in the building process if your docstring
has a `Methods` section in the class docstring
(see [#366](https://github.com/mkdocstrings/mkdocstrings/issues/366)).

You can see examples of Numpy-style docstrings
in [numpydoc's documentation](https://numpydoc.readthedocs.io/en/latest/format.html).

### reStructuredText-style

WARNING: **Partial support**  
Only RST-**style** is supported, not the whole RST markup specification.
 
You can see examples of reStructuredText-style docstrings
in [Sphinx's documentation](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).

#### Sections

Docstrings directives are parsed by `pytkdocs` and rendered by *mkdocstrings*.
Supported directives are:

- `param` (or `parameter`, `arg`, `argument`, `key`, `keyword`)
- `type`
- `raises` (or `raise`, `except`, `exception`)
- `var` (or `ivar`, `cvar`)
- `vartype`
- `returns` (or `return1`)
- `rtype`

Details about how to use each directive can be found in the
[Sphinx domain documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html?highlight=python%20domain#info-field-lists)

#### Annotations

Type annotations are read both in the code and in the docstrings.

> EXAMPLE: **Example with a function**  
> **Expand the source at the end to see the original code!**
>
> ::: snippets.function_annotations_rst:my_function
>     options:
>       docstring_style: restructured-text
>       show_root_heading: no
>       show_root_toc_entry: no

## Finding modules

There are multiple ways to tell the handler where to find your packages/modules.

**The recommended method is to use the `paths` option, as it's the only one
that works with the `-f` option of MkDocs, allowing to build the documentation
from any location on the file system.** Indeed, the paths provided with the
`paths` option are computed as relative to the configuration file (mkdocs.yml),
so that the current working directory has no impact on the build process:
*you can build the docs from any location on your filesystem*.

### Using the `paths` option

TIP: **This is the recommended method.**

1. mkdocs.yml in root, package in root
    ```tree
    root/
        mkdocs.yml
        package/
    ```

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            paths: [.]  # actually not needed, default
    ```

1. mkdocs.yml in root, package in subfolder
    ```tree
    root/
        mkdocs.yml
        src/
            package/
    ```

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            paths: [src]
    ```

1. mkdocs.yml in subfolder, package in root
    ```tree
    root/
        docs/
            mkdocs.yml
        package/
    ```

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            paths: [..]
    ```

1. mkdocs.yml in subfolder, package in subfolder
    ```tree
    root/
        docs/
            mkdocs.yml
        src/
            package/
    ```

    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            paths: [../src]
    ```

Except for case 1, which is supported by default, **we strongly recommend
to set the path to your packages using this option, even if it works without it**
(for example because your project manager automatically adds `src` to PYTHONPATH),
to make sure anyone can build your docs from any location on their filesystem.

Behind the scenes, the handler will actually insert the specified paths in front of `sys.path`.

### Using the PYTHONPATH environment variable

WARNING: **This method has limitations.**  
This method might work for you, with your current setup,
but not for others trying your build your docs with their own setup/environment.
We recommend to use the [`paths` method](#using-the-paths-option) instead.

You can take advantage of the usual Python loading mechanisms.
In Bash and other shells, you can run your command like this
(note the prepended `PYTHONPATH=...`):

1. mkdocs.yml in root, package in root
    ```tree
    root/
        mkdocs.yml
        package/
    ```

    ```bash
    PYTHONPATH=. mkdocs build  # actually not needed, default
    ```

1. mkdocs.yml in root, package in subfolder
    ```tree
    root/
        mkdocs.yml
        src/
            package/
    ```

    ```bash
    PYTHONPATH=src mkdocs build
    ```

1. mkdocs.yml in subfolder, package in root
    ```tree
    root/
        docs/
            mkdocs.yml
        package/
    ```

    ```bash
    PYTHONPATH=. mkdocs build -f docs/mkdocs.yml
    ```

1. mkdocs.yml in subfolder, package in subfolder
    ```tree
    root/
        docs/
            mkdocs.yml
        src/
            package/
    ```

    ```bash
    PYTHONPATH=src mkdocs build -f docs/mkdocs.yml
    ```
  
### Installing your package in the current Python environment

WARNING: **This method has limitations.**  
This method might work for you, with your current setup,
but not for others trying your build your docs with their own setup/environment.
We recommend to use the [`paths` method](#using-the-paths-option) instead.

Install your package in the current environment, and run MkDocs:

=== "pip"
    ```bash
    . venv/bin/activate
    pip install -e .
    mkdocs build
    ```

=== "PDM"
    ```bash
    pdm install
    pdm run mkdocs build
    ```

=== "Poetry"
    ```bash
    poetry install
    poetry run mkdocs build
    ```

### Using the setup commands

WARNING: **This method has limitations.**  
This method might work for you, with your current setup,
but not for others trying your build your docs with their own setup/environment.
We recommend to use the [`paths` method](#using-the-paths-option) instead.

You can use the setup commands to modify `sys.path`:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        setup_commands:
        - import sys
        - sys.path.append("src")
        # or sys.path.insert(0, "src")
```

## Mocking libraries

You may want to generate documentation for a package while its dependencies are not available.
The Python handler provides itself no builtin way to mock libraries,
but you can use the `setup_commands` to mock them manually:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        setup_commands:
        - import sys
        - from unittest.mock import MagicMock as mock
        - sys.modules["lib1"] = mock()
        - sys.modules["lib2"] = mock()
        - sys.modules["lib2.module1"] = mock()
        - sys.modules["lib2.module1.moduleB"] = mock()
        # etc
```

## Recommended style (Material)

Here are some CSS rules for the
[*Material for MkDocs*](https://squidfunk.github.io/mkdocs-material/) theme:

```css
/* Indentation. */
div.doc-contents:not(.first) {
  padding-left: 25px;
  border-left: .05rem solid var(--md-typeset-table-color);
}
```

## Recommended style (ReadTheDocs)

Here are some CSS rules for the built-in *ReadTheDocs* theme:

```css
/* Indentation. */
div.doc-contents:not(.first) {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
}
```
