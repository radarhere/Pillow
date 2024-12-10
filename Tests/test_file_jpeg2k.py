from __future__ import annotations

import os
import re
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from PIL import (
    Image,
    ImageFile,
    Jpeg2KImagePlugin,
    UnidentifiedImageError,
    _binary,
    features,
)

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    skip_unless_feature,
    skip_unless_feature_version,
)

EXTRA_DIR = "Tests/images/jpeg2000"

pytestmark = skip_unless_feature("jpg_2000")


@pytest.mark.skipif(
    not os.path.exists(EXTRA_DIR), reason="Extra image files not installed"
)
@skip_unless_feature_version("jpg_2000", "2.5.1")
def test_cmyk() -> None:
    with Image.open(f"{EXTRA_DIR}/issue205.jp2") as im:
        assert im.mode == "CMYK"
        assert im.getpixel((0, 0)) == (185, 134, 0, 0)
