from __future__ import annotations

import copy
import os
import re
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from PIL import Image, ImageDraw, ImageFont, features
from PIL._typing import StrOrBytesPath

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    is_win32,
    skip_unless_feature,
    skip_unless_feature_version,
)

FONT_PATH = "Tests/fonts/FreeMono.ttf"
FONT_SIZE = 20

TEST_TEXT = "hey you\nyou are awesome\nthis looks awkward"


pytestmark = skip_unless_feature("freetype2")


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        #pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request: pytest.FixtureRequest) -> ImageFont.Layout:
    return request.param


@pytest.fixture(scope="module")
def font(layout_engine: ImageFont.Layout) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=layout_engine)


def test_variation_set_by_axes(font: ImageFont.FreeTypeFont) -> None:
    with pytest.raises(OSError):
        font.set_variation_by_axes([500, 50])

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
    font.set_variation_by_axes([500, 50])
    _check_text(font, "Tests/images/variation_adobe_axes.png", 11.05)

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
    font.set_variation_by_axes([100])
    _check_text(font, "Tests/images/variation_tiny_axes.png", 32.5)
