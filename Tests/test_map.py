import sys

import pytest

from PIL import Image

from .helper import is_win32


def test_x():
    print("torchbefore")
    with Image.open("Tests/images/l2rgb_read.bmp") as im:
        im.tobytes()
    print("torchafter")
