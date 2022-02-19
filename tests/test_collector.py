#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from mkdocstrings.handlers.base import CollectionError
from mkdocstrings.handlers.python import collector


def test_init():
    assert collector.PythonCollector()


def test_collect():
    obj = collector.PythonCollector()
    with pytest.raises(CollectionError):
        obj.collect("", {})
