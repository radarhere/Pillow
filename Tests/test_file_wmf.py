from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_load_raw() -> None:
    # Test basic EMF open and rendering
    with Image.open("image94.emf") as im:
        im.load()
        print(im)
        width, height = im.size
        new_width = 400
        new_height = int((new_width / width) * height)
        resized_image = im.resize((new_width, new_height), Image.LANCZOS)
        print(resized_image)
        resized_image.save('out.png')
