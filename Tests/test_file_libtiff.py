from __future__ import annotations

import base64
import io
import itertools
import os
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from PIL import Image, ImageFilter, ImageOps, TiffImagePlugin, TiffTags, features
from PIL.TiffImagePlugin import OSUBFILETYPE, SAMPLEFORMAT, STRIPOFFSETS, SUBIFD

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    mark_if_feature_version,
    skip_unless_feature,
)


@skip_unless_feature("libtiff")
class LibTiffTestCase:
    def _assert_noerr(self, tmp_path: Path, im: TiffImagePlugin.TiffImageFile) -> None:
        """Helper tests that assert basic sanity about the g4 tiff reading"""
        # 1 bit
        assert im.mode == "1"

        # Does the data actually load
        im.load()
        im.getdata()

        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        assert im._compression == "group4"

        # can we write it back out, in a different form.
        out = tmp_path / "temp.png"
        im.save(out)

        out_bytes = io.BytesIO()
        im.save(out_bytes, format="tiff", compression="group4")


class TestFileLibTiff(LibTiffTestCase):
    def test_lzma(self, capfd: pytest.CaptureFixture[str]) -> None:
        with Image.open("Tests/images/hopper_lzma.tif") as im:
            im.load()
