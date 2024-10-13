from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_load_raw() -> None:
    # Test basic EMF open and rendering
    with Image.open("image94.emf") as im:
        width, height = im.size
        new_width = 400
        new_height = (new_width / width) * height
        if len(im.info["dpi"]) == 2:
            new_height /= im.info["dpi"][1] / im.info["dpi"][0]
        new_height = int(new_height)
        resized_image = im.resize((new_width, new_height), Image.LANCZOS)
        resized_image.save('out.png')
