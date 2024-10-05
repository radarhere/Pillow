from __future__ import annotations

import pytest

from PIL import Image, ImageStat

from .helper import hopper


def test_sanity() -> None:
    im = hopper()

    st = ImageStat.Stat(im)
    st = ImageStat.Stat(im.histogram())
    st = ImageStat.Stat(im, Image.new("1", im.size, 1))

    # Check these run. Exceptions will cause failures.
    st.extrema
    st.sum
    st.mean
    st.median
    st.rms
    st.sum2
    st.var
    st.stddev

    with pytest.raises(AttributeError):
        st.spam()  # type: ignore[attr-defined]

    with pytest.raises(TypeError):
        ImageStat.Stat(1)  # type: ignore[arg-type]


hopper_image_stats = {
    "RGB": {
        "sum": [1470218.0, 1311896.0, 1563008.0],
    },
    "HSV": {
        "sum": [0, 1958662.0, 1966497.0],
    }
}


@pytest.mark.parametrize("mode", hopper_image_stats.keys())
@pytest.mark.parametrize("stat", hopper_image_stats["RGB"].keys())
def test_hopper(mode: str, stat: str) -> None:
    im = hopper(mode)
    st = ImageStat.Stat(im)
    print(getattr(st, stat))
    assert getattr(st, stat) == hopper_image_stats[mode][stat]
