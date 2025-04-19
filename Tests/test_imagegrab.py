from __future__ import annotations

import os
import shutil
import subprocess
import sys

import pytest

from PIL import Image, ImageGrab

from .helper import assert_image_equal_tofile, skip_unless_feature


class TestImageGrab:
    def test_grab(self) -> None:
        print("before")
        ImageGrab.grab().save("grim.png")
        print("after")
