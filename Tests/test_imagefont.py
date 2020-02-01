import copy
import distutils.version
import os
import re
import shutil
import sys
import unittest
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, features

from .helper import PillowTestCase, is_pypy, is_win32, on_ci

FONT_PATH = "Tests/fonts/FreeMono.ttf"
FONT_SIZE = 20

TEST_TEXT = "hey you\nyou are awesome\nthis looks awkward"

HAS_FREETYPE = features.check("freetype2")
HAS_RAQM = features.check("raqm")


class SimplePatcher:
    def __init__(self, parent_obj, attr_name, value):
        self._parent_obj = parent_obj
        self._attr_name = attr_name
        self._saved = None
        self._is_saved = False
        self._value = value

    def __enter__(self):
        # Patch the attr on the object
        if hasattr(self._parent_obj, self._attr_name):
            self._saved = getattr(self._parent_obj, self._attr_name)
            setattr(self._parent_obj, self._attr_name, self._value)
            self._is_saved = True
        else:
            setattr(self._parent_obj, self._attr_name, self._value)
            self._is_saved = False

    def __exit__(self, type, value, traceback):
        # Restore the original value
        if self._is_saved:
            setattr(self._parent_obj, self._attr_name, self._saved)
        else:
            delattr(self._parent_obj, self._attr_name)


@unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
class TestImageFont(PillowTestCase):
    LAYOUT_ENGINE = ImageFont.LAYOUT_BASIC

    # Freetype has different metrics depending on the version.
    # (and, other things, but first things first)
    METRICS = {
        (">=2.3", "<2.4"): {"multiline": 30, "textsize": 12, "getters": (13, 16)},
        (">=2.7",): {"multiline": 6.2, "textsize": 2.5, "getters": (12, 16)},
        "Default": {"multiline": 0.5, "textsize": 0.5, "getters": (12, 16)},
    }

    def setUp(self):
        freetype = distutils.version.StrictVersion(ImageFont.core.freetype2_version)

        self.metrics = self.METRICS["Default"]
        for conditions, metrics in self.METRICS.items():
            if not isinstance(conditions, tuple):
                continue

            for condition in conditions:
                version = re.sub("[<=>]", "", condition)
                if (condition.startswith(">=") and freetype >= version) or (
                    condition.startswith("<") and freetype < version
                ):
                    # Condition was met
                    continue

                # Condition failed
                break
            else:
                # All conditions were met
                self.metrics = metrics

    #def test_stroke_multiline(self):
    #    # Arrange
    #    im = Image.new("RGB", (100, 250))
    #    draw = ImageDraw.Draw(im)
    #    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    #    # Act
    #    draw.multiline_text(
    #        (10, 10), "A\nB", "#f00", font, stroke_width=2, stroke_fill="#0f0"
    #    )

    #    # Assert
    #    im.save("Tests/errors/out_existing.jpg" if os.path.exists("Tests/errors") else "out_existing.jpg")
    #    self.assert_image_similar(
    #        im, Image.open("Tests/images/imagedraw_stroke_multiline.png"), 3.3
    #    )

    def test_torch(self):
        print()
        print("torch")

        font_path = "Tests/fonts/DejaVuSansMono.ttf"
        font_path2 = "Tests/fonts/FreeMono.ttf"
        image_color = (128,128,128)
        # Create an image with background color inverse to the text color.
        image = Image.new('RGB', (640, 480), color=image_color)
        text = "y"
        text_color_tuple = 255,0,0
        outline_color_tuple = 0,0,0
        font = ImageFont.truetype(font_path, size=48)
        font2 = ImageFont.truetype(font_path2, size=48)

        # Create the image to draw on.
        text_image = Image.new('RGB', image.size, (255, 255, 255))
        d = ImageDraw.Draw(text_image)
        print("torchA")
        d.multiline_text(
            xy=(0, 0),
            text=text,
            fill=text_color_tuple,
            font=font,
            stroke_width=1,
            stroke_fill=outline_color_tuple
        )
        print("torchB")
        if False:
            d.multiline_text(
                xy=(0, 200),
                text=text,
                fill=text_color_tuple,
                font=font2,
                stroke_width=1,
                stroke_fill=outline_color_tuple
            )
        x = sys.platform+"_"+ImageFont.core.freetype2_version
        text_image.save("Tests/errors/"+x+".png" if os.path.exists("Tests/errors") else x+".png")
        self.assertEqual("torch", ImageFont.core.freetype2_version)

    #def test_torch2(self):
    #    self.assertEqual("torch", ImageFont.core.freetype2_version)

#@unittest.skipUnless(HAS_RAQM, "Raqm not Available")
#class TestImageFont_RaqmLayout(TestImageFont):
#    LAYOUT_ENGINE = ImageFont.LAYOUT_RAQM
