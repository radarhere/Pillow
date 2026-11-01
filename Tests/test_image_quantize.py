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
def test_libimagequant_quantize() -> None:
    image = hopper()
    if is_ppc64le() and not has_feature_version("libimagequant", "4"):
        pytest.skip("Fails with libimagequant earlier than 4.0.0 on ppc64le")
    converted = image.quantize(100, Image.Quantize.LIBIMAGEQUANT)
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 15)
    colors = converted.getcolors()
    assert colors is not None
    assert len(colors) == 100
