from __future__ import annotations

import os
import re
import time
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from PIL import (
    Image,
    ImageFile,
    Jpeg2KImagePlugin,
    UnidentifiedImageError,
    _binary,
    features,
)

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    skip_unless_feature,
    skip_unless_feature_version,
)

def test_9bit() -> None:
    start = time.time()
    try:
        with Image.open("image") as im:
            im.load()
    except:
        pass
    print("Time taken:", time.time() - start)
