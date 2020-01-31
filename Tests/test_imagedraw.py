import os.path
import unittest

from PIL import Image, ImageColor, ImageDraw, ImageFont, features

from .helper import PillowTestCase, hopper

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DEFAULT_MODE = "RGB"
IMAGES_PATH = os.path.join("Tests", "images", "imagedraw")

# Image size
W, H = 100, 100

# Bounding box points
X0 = int(W / 4)
X1 = int(X0 * 3)
Y0 = int(H / 4)
Y1 = int(X0 * 3)

# Two kinds of bounding box
BBOX1 = [(X0, Y0), (X1, Y1)]
BBOX2 = [X0, Y0, X1, Y1]

# Two kinds of coordinate sequences
POINTS1 = [(10, 10), (20, 40), (30, 30)]
POINTS2 = [10, 10, 20, 40, 30, 30]

KITE_POINTS = [(10, 50), (70, 10), (90, 50), (70, 90), (10, 50)]

HAS_FREETYPE = features.check("freetype2")

if False:
    class TestImageDraw(PillowTestCase):
        @unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
        def test_stroke_multiline(self):
            # Arrange
            im = Image.new("RGB", (100, 250))
            draw = ImageDraw.Draw(im)
            font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

            # Act
            print("torchC")
            draw.multiline_text(
                (10, 10), "A\nB", "#f00", font, stroke_width=2, stroke_fill="#0f0"
            )

            # Assert
            im.save("Tests/errors/out_existing.jpg" if os.path.exists("Tests/errors") else "out_existing.jpg")
            self.assert_image_similar(
                im, Image.open("Tests/images/imagedraw_stroke_multiline.png"), 3.3
            )
