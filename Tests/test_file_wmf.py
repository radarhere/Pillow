from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_load() -> None:
    with Image.open("Tests/images/test.emf") as im:
        assert im.getpixel((0, 0)) == (255, 255, 255)
        assert im.getpixel((200, 200)) == (255, 255, 255)
