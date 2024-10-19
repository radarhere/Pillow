from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_6980() -> None:
    with Image.open("image94.emf") as im:
        im.load()
        print(im, im.info)
        im.save("out.png")
