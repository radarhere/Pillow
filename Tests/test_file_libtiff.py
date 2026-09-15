from __future__ import annotations

import base64
import io
import itertools
import os
import re
import sys
from typing import NamedTuple

import pytest

from PIL import (
    Image,
    ImageFile,
    ImageFilter,
    ImageOps,
    TiffImagePlugin,
    TiffTags,
    features,
)
from PIL.TiffImagePlugin import OSUBFILETYPE, SAMPLEFORMAT, STRIPOFFSETS, SUBIFD

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


@skip_unless_feature("libtiff")
class LibTiffTestCase:
    def _assert_noerr(self, tmp_path: Path, im: ImageFile.ImageFile) -> None:
        """Helper tests that assert basic sanity about the g4 tiff reading"""
        # 1 bit
        assert im.mode == "1"

        # Does the data actually load
        im.load()

        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        assert im._compression == "group4"

        # can we write it back out, in a different form.
        out = tmp_path / "temp.png"
        im.save(out)

        out_bytes = io.BytesIO()
        im.save(out_bytes, format="tiff", compression="group4")


class TestFileLibTiff(LibTiffTestCase):
    @pytest.mark.skipif(not os.path.isdir("/dev/fd"), reason="Requires /dev/fd")
    def test_save_compressed_no_fd_leak(self, tmp_path: Path) -> None:
        im = Image.new("L", (1, 1))
        out = tmp_path / "temp.tif"
        im.save(out, compression="jpeg")  # warmup
        fds = len(os.listdir("/dev/fd"))
        im.save(out, compression="jpeg")
        assert len(os.listdir("/dev/fd")) == fds
