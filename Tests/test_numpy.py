from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import pytest

from PIL import Image, ImageFilter, _typing

from .helper import assert_deep_equal, assert_image, hopper, skip_unless_feature

if TYPE_CHECKING:
    import numpy
    import numpy.typing as npt
else:
    numpy = pytest.importorskip("numpy", reason="NumPy not installed")

TEST_IMAGE_SIZE = (10, 10)


def test_8911() -> None:
    img = Image.open("Tests/images/hopper.png").convert("L")
    size = numpy.int64(2)
    img.filter(ImageFilter.GaussianBlur(radius = size))
