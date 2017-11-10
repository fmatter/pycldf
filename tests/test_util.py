# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest

from pycldf.util import multislice


@pytest.mark.parametrize("sliceable,slices,expected", [
    ('abcdefg', ['1:4', (1, 4)], 'bcdbcd'),
    ([1, 2, 3, 4], ['0:5:2'], [1, 3]),
    ((1, 2, 3, 4), ['0:5:2'], (1, 3))
])
def test_multislice(sliceable, slices, expected):
    assert multislice(sliceable, *slices) == expected
