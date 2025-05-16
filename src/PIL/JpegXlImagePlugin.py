from __future__ import annotations

from . import Image, ImageFile

try:
    from . import _jpegxl

    SUPPORTED = True
except ImportError:
    SUPPORTED = False


## Future idea:
## it's not known how many frames does animated image have
## by default, _jxl_decoder_new will iterate over all frames without decoding them
## then libjxl decoder is rewinded and we're ready to decode frame by frame
## if OPEN_COUNTS_FRAMES is False, n_frames will be None until the last frame is decoded
## it only applies to animated jpeg xl images
# OPEN_COUNTS_FRAMES = True


def _accept(prefix: bytes) -> bool:
    is_jxl = prefix.startswith(
        (b"\xff\x0a", b"\x00\x00\x00\x0c\x4a\x58\x4c\x20\x0d\x0a\x87\x0a")
    )
    if is_jxl and not SUPPORTED:
        msg = "image file could not be identified because JXL support not installed"
        raise SyntaxError(msg)
    return is_jxl


class JpegXlImageFile(ImageFile.ImageFile):
    format = "JPEG XL"
    format_description = "JPEG XL image"
    __loaded = 0
    __logical_frame = 0

    def _open(self) -> None:
        self._decoder = _jpegxl.JpegXlDecoder(self.fp.read())

        self._size = (1, 1)
        self._mode = "RGB"

        self._decoder.get_next()


Image.register_open(JpegXlImageFile.format, JpegXlImageFile, _accept)
Image.register_extension(JpegXlImageFile.format, ".jxl")
Image.register_mime(JpegXlImageFile.format, "image/jxl")
