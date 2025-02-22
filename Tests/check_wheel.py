from __future__ import annotations

import sys

from PIL import features


def test_wheel_modules() -> None:
    expected_modules = {"pil", "tkinter"}

    # tkinter is not available in cibuildwheel installed CPython on Windows
    try:
        import tkinter

        assert tkinter
    except ImportError:
        expected_modules.remove("tkinter")

    assert set(features.get_supported_modules()) == expected_modules


def test_wheel_codecs() -> None:
    expected_codecs = {"jpg", "zlib"}

    assert set(features.get_supported_codecs()) == expected_codecs


def test_wheel_features() -> None:
    expected_features = {
        "libjpeg_turbo",
        "zlib_ng",
    }

    assert set(features.get_supported_features()) == expected_features
