from __future__ import annotations

from PIL import Image

from .helper import skip_unless_feature

pytestmark = [skip_unless_feature("jpegxl")]


def test_float_duration() -> None:
    with Image.open("Tests/images/iss634.jxl"):
        pass
