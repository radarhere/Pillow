from __future__ import annotations

import math

import pytest

from PIL import Image, ImageFilter

from .helper import assert_image_equal, hopper


def test_large_blur_filter_radius() -> None:
    radius = 2**31
    # A radius this large overflows the accumulators unless they stay unsigned
    im = Image.new("L", (3, 3), 128)
    assert im.filter(ImageFilter.BoxBlur(radius)).getpixel((1, 1)) == 128

    im = Image.new("RGB", (3, 3), (128, 128, 128))
    assert im.filter(ImageFilter.BoxBlur(radius)).getpixel((1, 1)) == (128, 128, 128)
