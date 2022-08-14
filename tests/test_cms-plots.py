#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cms_plots` package."""

import pytest  # noqa: F401
import cms_plots  # noqa: F401


def test_construction():
    """Just create an object and test its type."""
    result = cms_plots.Figure()
    assert str(type(result)) == "<class 'cms_plots.plotting.Figure'>"
