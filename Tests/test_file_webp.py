from __future__ import annotations

import io
import re
import sys
import time
import warnings
from pathlib import Path
from typing import Any

import pytest

from PIL import Image, WebPImagePlugin, features

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


@skip_unless_feature("webp")
class TestFileWebp:
    def test_speed(self) -> None:
        with Image.open("Tests/images/iss634.gif") as im:
            im.load()
            assert im.n_frames == 42

            start = time.time()
            for _ in range(100):
                im.save("out.webp", save_all=True)
            print("Time taken: "+str(time.time() - start))
