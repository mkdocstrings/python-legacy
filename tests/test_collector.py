# -*- coding: utf-8 -*-
"""test for mkdocstrings.handlers.python.collector."""
from unittest import mock

import pytest

from mkdocstrings.handlers.base import CollectionError
from mkdocstrings.handlers.python import collector


def test_init():
    """Test init for collector.PythonCollector."""
    assert collector.PythonCollector()


@pytest.mark.parametrize(
    ("retval", "exp_res"),
    [
        ({"error": "error1", "traceback": "hello"}, "error1\nhello"),
        ({"error": "error1"}, "error1"),
        ({"error": "", "traceback": "hello"}, "\nhello"),
    ],
)
def test_collect_result_error(retval, exp_res):
    """Test handling of errors when collecting an object.

    Args:
        retval: return value to mock json.loads
        exp_res: expected result
    """
    with mock.patch("mkdocstrings.handlers.python.collector.json.loads") as m_loads:
        with pytest.raises(CollectionError) as excinfo:  # noqa: PT012
            m_loads.return_value = retval
            obj = collector.PythonCollector()
            assert obj.collect("", {})
            assert str(excinfo.value) == exp_res
