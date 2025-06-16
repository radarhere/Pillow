from __future__ import annotations

import io
from pathlib import Path

import pytest

from PIL import Image, TiffImagePlugin

from .helper import (
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
    def test_crashing_metadata(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # issue 1597
        print("start")
        with Image.open("Tests/images/rdf.tif") as im:
            out = tmp_path / "temp.tif"

            # this shouldn't crash
            print(im.tag_v2[318])
            im.save(out, format="TIFF", tag_v2=im.tag_v2)
            with Image.open(out) as re:
                print(re.tag_v2[318])
