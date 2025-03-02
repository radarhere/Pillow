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


@pytest.fixture
def card() -> Generator[ImageFile.ImageFile, None, None]:
    with Image.open("Tests/images/test-card.png") as im:
        im.load()
    try:
        yield im
    finally:
        im.close()


# OpenJPEG 2.0.0 outputs this debugging message sometimes; we should
# ignore it---it doesn't represent a test failure.
# 'Not enough memory to handle tile data'


def roundtrip(im: Image.Image, **options: Any) -> Image.Image:
    out = BytesIO()
    im.save(out, "JPEG2000", **options)
    out.seek(0)
    with Image.open(out) as im:
        im.load()
    return im


def test_9bit() -> None:
    with Image.open("000137.jp2") as im:
        im.load()
        print(im)
