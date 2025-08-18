from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, skip_unless_feature

pytestmark = [skip_unless_feature("jpegxl")]


def test_float_duration() -> None:
    with Image.open("Tests/images/iss634.jxl") as im:
        pass
