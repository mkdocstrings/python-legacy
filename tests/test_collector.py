"""Tests for the `collector` module."""

from unittest import mock

import pytest
from mkdocstrings import CollectionError

from mkdocstrings_handlers.python import get_handler


class _FakeMkDocsConfig:
    config_file_path = "mkdocs.yml"


@pytest.mark.parametrize(
    ("retval", "exp_res"),
    [
        ({"error": "error1", "traceback": "hello"}, "error1\nhello"),
        ({"error": "error1"}, "error1"),
        ({"error": "", "traceback": "hello"}, "\nhello"),
    ],
)
def test_collect_result_error(retval: dict, exp_res: str) -> None:
    """Test handling of errors when collecting an object.

    Args:
        retval: Return value to mock `json.loads` with.
        exp_res: Expected result.
    """
    with mock.patch("mkdocstrings_handlers.python.handler.json.loads") as m_loads:  # noqa: SIM117
        with pytest.raises(CollectionError) as excinfo:  # noqa: PT012
            m_loads.return_value = retval
            handler = get_handler({}, _FakeMkDocsConfig, theme="material")  # type: ignore[arg-type]
            assert handler.collect("", {})
            assert str(excinfo.value) == exp_res
