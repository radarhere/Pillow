from __future__ import annotations

import pytest

from PIL import Image, ImageStat

from .helper import hopper


def test_hopper() -> None:
    im = hopper("HSV").crop((10, 15, 20, 20))
    #with open("out", "wb") as fp:
    #    fp.write(im.tobytes())
    with open("out", "rb") as fp:
        assert fp.read() == im.tobytes()










