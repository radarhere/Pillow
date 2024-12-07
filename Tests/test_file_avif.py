from __future__ import annotations

import gc
import os
import re
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from struct import unpack
from typing import Any

import pytest

from PIL import (
    AvifImagePlugin,
    Image,
    ImageDraw,
    ImageFile,
    UnidentifiedImageError,
    features,
)

from .helper import (
    PillowLeakTestCase,
    assert_image,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

try:
    from PIL import _avif

    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False


@skip_unless_feature("avif")
class TestFileAvif:
    def test_exif(self) -> None:
        # With an EXIF chunk
        with Image.open("Tests/images/avif/exif.avif") as im:
            exif = im.getexif()
        assert exif[274] == 1

        im.save("out.avif", exif=exif)
        assert_image_similar_tofile(im, "out.avif", 3)

        with Image.open("Tests/images/avif/xmp_tags_orientation.avif") as im:
            im.save("original.png")
            exif = im.getexif()
        assert exif[274] == 3

        im.save("out2.avif", exif=exif)
        reloaded = Image.open("out2.avif")
        print("out2 orientation", reloaded.getexif().get(274))
        reloaded.load()
        reloaded.save("reloaded.png")

        #assert_image_similar_tofile(im, "out2.avif", 3)

