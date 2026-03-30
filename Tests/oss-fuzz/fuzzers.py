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
    Image.frombuffer('P', (9,1), b'\xAB\xCD\xEF\x12\x34', 'raw', 'P;4L', 0, 1).load()


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
