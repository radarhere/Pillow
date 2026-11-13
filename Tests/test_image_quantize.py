from __future__ import annotations

import pytest

from PIL import Image

from .helper import (
    assert_image_similar,
    has_feature_version,
    hopper,
    is_ppc64le,
    skip_unless_feature,
)



@skip_unless_feature("libimagequant")
def test_resize() -> None:
    im = hopper().resize((100, 100))
    try:
        im.quantize(100, Image.Quantize.LIBIMAGEQUANT)
    except ValueError:
        pass
