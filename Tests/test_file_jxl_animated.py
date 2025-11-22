from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, skip_unless_feature

pytestmark = [skip_unless_feature("jpegxl")]


def test_n_frames() -> None:
    """Ensure that jxl format sets n_frames and is_animated attributes correctly."""

    with Image.open("Tests/images/hopper.jxl") as im:
        assert im.n_frames == 1
        assert not im.is_animated

    with Image.open("Tests/images/iss634.jxl") as im:
        assert im.n_frames == 41
        assert im.is_animated
