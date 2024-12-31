from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest

from PIL import (
    BmpImagePlugin,
    EpsImagePlugin,
    Image,
    ImageFile,
    UnidentifiedImageError,
    _binary,
    features,
)

from .helper import (
    assert_image,
    assert_image_equal,
    assert_image_similar,
    fromstring,
    hopper,
    skip_unless_feature,
    tostring,
)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK


class TestImageFile:
    def test_parser(self) -> None:
        def roundtrip(format: str) -> tuple[Image.Image, Image.Image]:
            im = hopper("L").resize((1000, 1000), Image.Resampling.NEAREST)
            if format in ("MSP", "XBM"):
                im = im.convert("1")

            test_file = BytesIO()

            im.copy().save(test_file, format)

        if features.check("jpg"):
            roundtrip("JPEG")
