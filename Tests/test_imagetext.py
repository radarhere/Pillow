from __future__ import annotations

import pytest

from PIL import Image, ImageDraw, ImageFont, ImageText

from .helper import assert_image_similar_tofile, skip_unless_feature

FONT_PATH = "Tests/fonts/FreeMono.ttf"


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request: pytest.FixtureRequest) -> ImageFont.Layout:
    return request.param


@pytest.fixture(scope="module")
def font(layout_engine: ImageFont.Layout) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, 20, layout_engine=layout_engine)


@skip_unless_feature("freetype2")
def test_get_length(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.Text("A", font).get_length() == 12
    assert ImageText.Text("AB", font).get_length() == 24
    assert ImageText.Text("M", font).get_length() == 12
    assert ImageText.Text("y", font).get_length() == 12
    assert ImageText.Text("a", font).get_length() == 12

    text = ImageText.Text("\n", font)
    with pytest.raises(ValueError, match="can't measure length of multiline text"):
        text.get_length()


@skip_unless_feature("freetype2")
def test_get_bbox(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.Text("A", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.Text("AB", font).get_bbox() == (0, 4, 24, 16)
    assert ImageText.Text("M", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.Text("y", font).get_bbox() == (0, 7, 12, 20)
    assert ImageText.Text("a", font).get_bbox() == (0, 7, 12, 16)


@skip_unless_feature("freetype2")
def test_standard_embedded_color(layout_engine: ImageFont.Layout) -> None:
    font = ImageFont.truetype(FONT_PATH, 40, layout_engine=layout_engine)
    text = ImageText.Text("Hello World!", font)
    text.embed_color()
    assert text.get_length() == 288

    im = Image.new("RGB", (300, 64), "white")
    draw = ImageDraw.Draw(im)
    draw.text((10, 10), text, "#fa6")

    assert_image_similar_tofile(im, "Tests/images/standard_embedded.png", 3.1)

    text = ImageText.Text("", mode="1")
    with pytest.raises(
        ValueError, match="Embedded color supported only in RGB and RGBA modes"
    ):
        text.embed_color()


@skip_unless_feature("freetype2")
def test_stroke() -> None:
    for suffix, stroke_fill in {"same": None, "different": "#0f0"}.items():
        # Arrange
        im = Image.new("RGB", (120, 130))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(FONT_PATH, 120)
        text = ImageText.Text("A", font)
        text.stroke(2, stroke_fill)

        # Act
        draw.text((12, 12), text, "#f00")

        # Assert
        assert_image_similar_tofile(
            im, "Tests/images/imagedraw_stroke_" + suffix + ".png", 3.1
        )


@pytest.mark.parametrize(
    "data, width, expected",
    (
        ("Hello World!", 100, "Hello World!"),  # No wrap required
        ("Hello World!", 50, "Hello\nWorld!"),  # Wrap word to a new line
        # Keep multiple spaces within a line
        ("Keep  multiple spaces", 75, "Keep  multiple\nspaces"),
        (" Keep\n leading space", 100, " Keep\n leading space"),
    ),
)
@pytest.mark.parametrize("string", (True, False))
def test_wrap(data: str, width: int, expected: str, string: bool) -> None:
    if string:
        text = ImageText.Text(data)
        assert text.wrap(width) is None
        assert text.text == expected
    else:
        text_bytes = ImageText.Text(data.encode())
        assert text_bytes.wrap(width) is None
        assert text_bytes.text == expected.encode()


def test_wrap_long_word() -> None:
    text = ImageText.Text("Hello World!")
    with pytest.raises(ValueError, match="Word does not fit within line"):
        text.wrap(25)


def test_wrap_unsupported(font: ImageFont.FreeTypeFont) -> None:
    transposed_font = ImageFont.TransposedFont(font)
    text = ImageText.Text("Hello World!", transposed_font)
    with pytest.raises(ValueError, match="TransposedFont not supported"):
        text.wrap(50)

    text = ImageText.Text("Hello World!", direction="ttb")
    with pytest.raises(ValueError, match="Only ltr direction supported"):
        text.wrap(50)


def test_wrap_height() -> None:
    text = ImageText.Text("Text does not fit within height")
    wrapped = text.wrap(50, 25)
    assert wrapped is not None
    assert wrapped.text == " within height"
    assert text.text == "Text does\nnot fit"


def test_wrap_scaling_unsupported() -> None:
    font = ImageFont.load_default_imagefont()
    text = ImageText.Text("Hello World!", font)
    with pytest.raises(ValueError, match="'scaling' only supports FreeTypeFont"):
        text.wrap(50, scaling="shrink")

    text = ImageText.Text("Hello World!")
    with pytest.raises(ValueError, match="'scaling' requires 'height'"):
        text.wrap(50, scaling="shrink")


def test_wrap_shrink() -> None:
    # No scaling required
    text = ImageText.Text("Hello World!")
    assert text.wrap(50, 50, "shrink") is None
    assert isinstance(text.font, ImageFont.FreeTypeFont)
    assert text.font.size == 10

    with pytest.raises(ValueError, match="Text could not be scaled"):
        text.wrap(50, 15, ("shrink", 9))

    assert text.wrap(50, 15, "shrink") is None
    assert text.font.size == 8

    text = ImageText.Text("Hello World!")
    assert text.wrap(50, 15, ("shrink", 7)) is None
    assert isinstance(text.font, ImageFont.FreeTypeFont)
    assert text.font.size == 8


def test_wrap_grow() -> None:
    # No scaling required
    text = ImageText.Text("Hello World!")
    assert text.wrap(58, 10, "grow") is None
    assert isinstance(text.font, ImageFont.FreeTypeFont)
    assert text.font.size == 10

    with pytest.raises(ValueError, match="Text could not be scaled"):
        text.wrap(50, 50, ("grow", 12))

    assert text.wrap(50, 50, "grow") is None
    assert text.font.size == 16

    text = ImageText.Text("Hello World!")
    assert text.wrap(50, 50, ("grow", 18)) is None
    assert isinstance(text.font, ImageFont.FreeTypeFont)
    assert text.font.size == 16
