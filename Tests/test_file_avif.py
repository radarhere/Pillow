from __future__ import annotations

from io import BytesIO

import pytest

from PIL import (
    Image,
)

from .helper import (
    skip_unless_feature,
)

try:
    from PIL import _avif

    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False


def skip_unless_avif_encoder(codec_name: str) -> pytest.MarkDecorator:
    reason = f"{codec_name} encode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.encoder_codec_available(codec_name), reason=reason
    )


@skip_unless_feature("avif")
class TestFileAvif:
    @skip_unless_avif_encoder("aom")
    def test_encoder_advanced_codec_options(self) -> None:
        with Image.open("Tests/images/avif/hopper.avif") as im:
            test_buf = BytesIO()
            im.save(
                test_buf,
                "AVIF",
                codec="aom",
            )
            ctrl_buf = BytesIO()
            im.save(
                ctrl_buf,
                "AVIF",
                codec="aom",
                advanced={"enable-chroma-deltaq": "0"},
            )
            if ctrl_buf.getvalue() == test_buf.getvalue():
                print("enable-chroma-deltaq=0 is the default behaviour")
            else:
                ctrl_buf1 = BytesIO()
                im.save(
                    ctrl_buf1,
                    "AVIF",
                    codec="aom",
                    advanced={"enable-chroma-deltaq": "1"},
                )
                if ctrl_buf1.getvalue() == test_buf.getvalue():
                    print("enable-chroma-deltaq=1 is the default behaviour")
                else:
                    print("enable-chroma-deltaq=0 is not the default behaviour")
                assert False
