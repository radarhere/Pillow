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


def test_8062() -> None:
    Image.open("cmyk.tif").save("out.jp2")
