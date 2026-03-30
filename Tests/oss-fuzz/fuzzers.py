from __future__ import annotations

import io
import warnings

from PIL import Image, ImageDraw, ImageFile, ImageFilter, ImageFont


def enable_decompressionbomb_error() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    warnings.filterwarnings("ignore")
    warnings.simplefilter("error", Image.DecompressionBombWarning)


def disable_decompressionbomb_error() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    warnings.resetwarnings()


def fuzz_image(data: bytes) -> None:
    # P;4L (4-bit)
    data = b'\xAB\xCD\xEF\x12\x34'
    img = Image.frombuffer("P", (9,1), data, "raw", "P;4L", 0, 1)
    img.load()
    list(img.getdata())
    # Output includes values not from input (heap leakage)

    # P;2L (2-bit)
    data2 = b'\xAB\xCD\x00'
    img2 = Image.frombuffer("P", (9,1), data2, "raw", "P;2L", 0, 1)
    img2.load()
    list(img2.getdata())


def fuzz_font(data: bytes) -> None:
    wrapper = io.BytesIO(data)
    try:
        font = ImageFont.truetype(wrapper)
    except OSError:
        # Catch pcf/pilfonts/random garbage here. They return
        # different font objects.
        return

    font.getbbox("ABC")
    font.getmask("test text")
    with Image.new(mode="RGBA", size=(200, 200)) as im:
        draw = ImageDraw.Draw(im)
        draw.multiline_textbbox((10, 10), "ABC\nAaaa", font, stroke_width=2)
        draw.text((10, 10), "Test Text", font=font, fill="#000")
