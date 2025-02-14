from __future__ import annotations

import io
import logging
import os
import shutil
import sys
import tempfile
import warnings
from pathlib import Path
from types import ModuleType
from typing import IO, Any

import pytest

from PIL import (
    ExifTags,
    Image,
    ImageDraw,
    ImageFile,
    ImagePalette,
    UnidentifiedImageError,
    features,
)

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    assert_not_all_same,
    hopper,
    is_big_endian,
    is_win32,
    mark_if_feature_version,
    skip_unless_feature,
)

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None

PrettyPrinter: type | None
try:
    from IPython.lib.pretty import PrettyPrinter
except ImportError:
    PrettyPrinter = None


# Deprecation helper
def helper_image_new(mode: str, size: tuple[int, int]) -> Image.Image:
    if mode.startswith("BGR;"):
        with pytest.warns(DeprecationWarning):
            return Image.new(mode, size)
    else:
        return Image.new(mode, size)


class TestImage:
    def test_8749(self):
        size = (16, 16)
        im = Image.new("RGB", size, "black")
        draw = ImageDraw.Draw(im)
        draw.ellipse((0, 0, size[0] - 1, size[1] - 1), fill="red")

        b = io.BytesIO()
        im.save(b, format="PNG")
        import hashlib
        m = hashlib.sha256()
        m.update(b.getvalue())
        assert m.hexdigest() == "1e8eb4ff3e6193c5a21b49b99209bc4774fb72286d91de96f3d187769effbc33"
