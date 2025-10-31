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


def test_get_length(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.Text("A", font).get_length() == 12
    assert ImageText.Text("AB", font).get_length() == 24
    assert ImageText.Text("M", font).get_length() == 12
    assert ImageText.Text("y", font).get_length() == 12
    assert ImageText.Text("a", font).get_length() == 12

    text = ImageText.Text("\n", font)
    with pytest.raises(ValueError, match="can't measure length of multiline text"):
        text.get_length()


def test_get_bbox(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.Text("A", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.Text("AB", font).get_bbox() == (0, 4, 24, 16)
    assert ImageText.Text("M", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.Text("y", font).get_bbox() == (0, 7, 12, 20)
    assert ImageText.Text("a", font).get_bbox() == (0, 7, 12, 16)


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
    "text, width, expected",
    (
        ("Hello World!", 100, "Hello World!"),  # No wrap required
        ("Hello World!", 50, "Hello\nWorld!"),  # Wrap word to a new line
        ("Hello World!", 25, "Hello\nWorl\nd!"),  # Split word across lines
        # Keep multiple spaces within a line
        ("Keep  multiple spaces", 75, "Keep  multiple\nspaces"),
    ),
)
@pytest.mark.parametrize("string", (True, False))
def test_wrap(text: str, width: int, expected: str, string: bool) -> None:
    text = ImageText.Text(text if string else text.encode())
    assert text.wrap(width) is None
    assert text.text == expected if string else expected.encode()


def test_wrap_height() -> None:
    text = ImageText.Text("Text does not fit within height")
    assert text.wrap(50, 25).text == " within height"
    assert text.text == "Text does\nnot fit"

    text = ImageText.Text("Text does not fit singlelongword")
    assert text.wrap(50, 25).text == " singlelongword"
    assert text.text == "Text does\nnot fit"
