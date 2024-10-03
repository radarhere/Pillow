from __future__ import annotations

from PIL import Image

from .helper import hopper


def test_sanity() -> None:
    with open("out", "rb") as f:
        assert hopper().convert("HSV").tobytes() == f.read()
