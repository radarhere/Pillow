import io
import os
import re

import pytest
from PIL import Image, WebPImagePlugin, features

from .helper import (
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestUnsupportedWebp:
    def test_unsupported(self):
        if HAVE_WEBP:
            WebPImagePlugin.SUPPORTED = False

        file_path = "Tests/images/hopper.webp"
        pytest.warns(UserWarning, lambda: pytest.raises(OSError, Image.open, file_path))

        if HAVE_WEBP:
            WebPImagePlugin.SUPPORTED = True


@skip_unless_feature("webp")
class TestFileWebp:
    def setup_method(self):
        self.rgb_mode = "RGB"

    def test_version(self):
        _webp.WebPDecoderVersion()
        _webp.WebPDecoderBuggyAlpha()
        assert re.search(r"\d+\.\d+\.\d+$", features.version_module("webp"))

    def test_read_rgb(self):
        source = Image.open('Tests/images/source.jpg')
        source.save('dest.webp', quality=80)
        print(["TORCH",os.path.getsize('dest.webp')])
