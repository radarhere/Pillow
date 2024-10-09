from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_load() -> None:
    with Image.open("test.emf") as im:
        im.save("out.png")
