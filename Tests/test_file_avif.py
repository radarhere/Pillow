from __future__ import annotations

import gc
import os
import re
import warnings
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from PIL import (
    AvifImagePlugin,
    GifImagePlugin,
    Image,
    ImageDraw,
    ImageFile,
    UnidentifiedImageError,
    features,
)

from .helper import (
    PillowLeakTestCase,
    assert_image,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
    skip_unless_feature_version,
)

try:
    from PIL import _avif

    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False


TEST_AVIF_FILE = "Tests/images/avif/hopper.avif"


def assert_xmp_orientation(xmp: bytes, expected: int) -> None:
    assert int(xmp.split(b'tiff:Orientation="')[1].split(b'"')[0]) == expected


def roundtrip(im: Image.Image, **options: Any) -> ImageFile.ImageFile:
    out = BytesIO()
    im.save(out, "AVIF", **options)
    return Image.open(out)


def skip_unless_avif_decoder(codec_name: str) -> pytest.MarkDecorator:
    reason = f"{codec_name} decode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.decoder_codec_available(codec_name), reason=reason
    )


def skip_unless_avif_encoder(codec_name: str) -> pytest.MarkDecorator:
    reason = f"{codec_name} encode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.encoder_codec_available(codec_name), reason=reason
    )


def is_docker_qemu() -> bool:
    try:
        init_proc_exe = os.readlink("/proc/1/exe")
    except (FileNotFoundError, PermissionError):
        return False
    return "qemu" in init_proc_exe


class TestUnsupportedAvif:
    def test_unsupported(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        with pytest.raises(UnidentifiedImageError):
            with pytest.warns(UserWarning, match="AVIF support not installed"):
                with Image.open(TEST_AVIF_FILE):
                    pass

    def test_unsupported_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        with pytest.raises(SyntaxError):
            AvifImagePlugin.AvifImageFile(TEST_AVIF_FILE)


@skip_unless_feature("avif")
class TestFileAvif:
    def test_version(self) -> None:
        version = features.version_module("avif")
        assert version is not None
        assert re.search(r"^\d+\.\d+\.\d+$", version)

    @skip_unless_feature_version("avif", "1.3.0")
    def test_write_l(self) -> None:
        im = hopper("L")
        reloaded = roundtrip(im)

        assert reloaded.mode == "L"
        assert_image_similar(reloaded, im, 1.67)


MAX_THREADS = os.cpu_count() or 1


@skip_unless_feature("avif")
class TestAvifLeaks(PillowLeakTestCase):
    mem_limit = MAX_THREADS * 3 * 1024
    iterations = 100

    @pytest.mark.skipif(
        is_docker_qemu(), reason="Skipping on cross-architecture containers"
    )
    def test_leak_load(self) -> None:
        with open(TEST_AVIF_FILE, "rb") as f:
            im_data = f.read()

        def core() -> None:
            with Image.open(BytesIO(im_data)) as im:
                im.load()
            gc.collect()

        self._test_leak(core)
