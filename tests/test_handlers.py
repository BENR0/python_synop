#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test decoding handlers."""

#import pytest
import numpy as np
from synop.handlers import handle_sTTT


def test_sTTT():
    """Test temperature decoding."""
    code = "////"
    res = handle_sTTT(code)
    assert np.isnan(res)

    code = "0/12"
    res = handle_sTTT(code)
    assert np.isnan(res)

    code = "0123"
    res = handle_sTTT(code)
    assert res == 12.3

    code = "1154"
    res = handle_sTTT(code)
    assert res == -15.4
