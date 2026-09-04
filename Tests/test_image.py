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
    mark_if_feature_version,
    skip_unless_feature,
    timeout_unless_slower_valgrind,
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
    @pytest.mark.parametrize("mode", ("L", "I", "F"))
    @pytest.mark.parametrize(
        "size, expected",
        (
            (2**31 - 1, (1, 1)),
            ((2**31 - 1, 1), (1, 10)),
            ((1, 2**31 - 1), (10, 1)),
        ),
    )
    def test_args_factor_large(
        self, size: int | tuple[int, int], expected: tuple[int, int], mode: str
    ) -> None:
        im = Image.new(mode, (10, 10))
        assert im.reduce(size).size == expected
