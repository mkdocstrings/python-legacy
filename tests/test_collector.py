#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest import mock

import pytest

from mkdocstrings.handlers.base import CollectionError
from mkdocstrings.handlers.python import collector


def test_init():
    collector.PythonCollector()


@pytest.mark.parametrize(
    "retval, exp_res",
    (
        ({"error": "error1", "traceback": "hello"}, "error1\nhello"),
        ({"error": "error1"}, "error1"),
    ),
)
def test_collect_result_error(retval, exp_res):
    with mock.patch("mkdocstrings.handlers.python.collector.json.loads") as m_loads, pytest.raises(
        CollectionError
    ) as excinfo:
        m_loads.return_value = retval
        obj = collector.PythonCollector()
        assert obj.collect("", {})
    assert str(excinfo.value) == exp_res
