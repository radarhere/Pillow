from __future__ import annotations

import io
import logging
import os
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

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
    is_win32,
    skip_unless_feature,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from types import ModuleType
    from typing import IO

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


class TestImage:
    @pytest.mark.parametrize("mode", ("I;16", "I;16L", "I;16B", "I;16N"))
    def test_i16_conversion(self, mode: str) -> None:
        im = Image.new(mode, (1, 1), 200)
        assert im.getpixel((0, 0)) == 200
        im_l2 = im.convert("L")
        assert im_l2.getpixel((0, 0)) == 200
