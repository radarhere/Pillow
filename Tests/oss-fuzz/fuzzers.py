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
    # This will fail on some images in the corpus, as we have many
    # invalid images in the test suite.
    with Image.open(io.BytesIO(data)) as im:
        im.rotate(45)
        im.filter(ImageFilter.DETAIL)
        im.save(io.BytesIO(), "BMP")


def fuzz_font(data: str) -> None:
    try:
        ImageFont.truetype(data)
    except OSError:
        # Catch pcf/pilfonts/random garbage here. They return
        # different font objects.
        return
