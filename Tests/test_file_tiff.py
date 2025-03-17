from __future__ import annotations

import os
import warnings
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from types import ModuleType

import pytest

from PIL import Image, ImageFile, TiffImagePlugin, UnidentifiedImageError
from PIL.TiffImagePlugin import RESOLUTION_UNIT, X_RESOLUTION, Y_RESOLUTION

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    is_pypy,
    is_win32,
)

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None


class TestFileTiff:
    @pytest.mark.timeout(6)
    @pytest.mark.filterwarnings("ignore:Truncated File Read")
    def test_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import time
        start = time.time()
        with Image.open("Tests/images/timeout-6646305047838720") as im:
            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
        print(time.time() - start)
