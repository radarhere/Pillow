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


def test_sanity() -> None:
    version = features.version_module("freetype2")
    assert version is not None
    assert re.search(r"\d+\.\d+\.\d+$", version)


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request: pytest.FixtureRequest) -> ImageFont.Layout:
    return request.param


@pytest.fixture(scope="module")
def font(layout_engine: ImageFont.Layout) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=layout_engine)


def _render(
    font: StrOrBytesPath | BinaryIO, layout_engine: ImageFont.Layout
) -> Image.Image:
    txt = "Hello World!"
    ttf = ImageFont.truetype(font, FONT_SIZE, layout_engine=layout_engine)
    ttf.getbbox(txt)


@pytest.mark.parametrize("font", (FONT_PATH, Path(FONT_PATH)))
def test_font_with_name(layout_engine: ImageFont.Layout, font: str | Path) -> None:
    _render(font, layout_engine)

