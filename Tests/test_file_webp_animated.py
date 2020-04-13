import pytest
from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_similar,
    is_big_endian,
    on_ci,
    skip_unless_feature,
)

pytestmark = [
    skip_unless_feature("webp"),
    skip_unless_feature("webp_anim"),
]


def test_write_animation_L(tmp_path):
    """
    Convert an animated GIF to animated WebP, then compare the frame count, and first
    and last frames to ensure they're visually similar.
    """

    with Image.open("Tests/images/iss634.gif") as orig:
        assert orig.n_frames > 1

        temp_file = str(tmp_path / "temp.webp")
        orig.save(temp_file, save_all=True)
        with Image.open(temp_file) as im:
            assert im.n_frames == orig.n_frames
            print(im.mode)

            # Compare first and last frames to the original animated GIF
            orig.load()
            im.load()
            assert_image_similar(im, orig.convert("RGBA"), 25.0)
            orig.seek(orig.n_frames - 1)
            im.seek(im.n_frames - 1)
            orig.load()
            im.load()
            assert_image_similar(im, orig.convert("RGBA"), 25.0)
