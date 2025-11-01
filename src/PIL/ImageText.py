from __future__ import annotations

from typing import AnyStr, Generic, NamedTuple, cast

from . import ImageFont
from ._typing import _Ink


class _Line(NamedTuple):
    x: float
    y: float
    anchor: str
    text: str | bytes


class _Wrap(Generic[AnyStr]):
    wrapped_lines: list[str] | list[bytes] = []
    reached_end = False
    remaining_position = 0

    def __init__(self, text: Text, width: int, height: int | None = None) -> None:
        emptystring = "" if isinstance(self.text.text, str) else b""
        newline = "\n" if isinstance(self.text.text, str) else b"\n"

        wrapped_line = emptystring
        word = emptystring

        for i in range(len(self.text.text)):
            last_character = i == len(self.text.text) - 1
            character = self.text.text[i : i + 1]
            if last_character:
                word += character
                character = newline
            if character.isspace():
                if not word or word.isspace():
                    # Do not use whitespace until a non-whitespace character is reached
                    # Trimming whitespace from the end of the line
                    word += character
                else:
                    # Append the word to the current line
                    if not wrapped_line:
                        word = word.lstrip()
                    new_wrapped_line = wrapped_line + word
                    if self.text._get_bbox(new_wrapped_line)[2] > width:

                        if wrapped_line:
                            # This word does not fit on the line
                            if not self.add_line():
                                reached_end = True
                                break
                            word = word.lstrip()
                            if self.text._get_bbox(word)[2] > width:
                                self.split_word()
                            else:
                                wrapped_line = word
                        else:
                            self.split_word()
                        if reached_end:
                            break
                    else:
                        # This word fits on the line
                        wrapped_line = new_wrapped_line
                        word = emptystring

                    word = emptystring if character == newline else character

            if character == newline:
                if not self.add_line():
                    break
                wrapped_line = emptystring
            elif not character.isspace():
                # Word is not finished yet
                word += character

    def add_line(self) -> bool:
        lines = cast(
            list[str] | list[bytes], self.wrapped_lines + [wrapped_line.rstrip()]
        )
        if height is not None:
            last_line_y = self._split(lines=lines)[-1].y
            last_line_height = self.text._get_bbox(wrapped_line)[3]
            if last_line_y + last_line_height > height:
                return False

        self.wrapped_lines = lines
        self.remaining_position = i - len(word)
        if last_character:
            self.remaining_position += 1
        return True

    def split_word(self) -> None:
        # This word is too long for a single line, so split the word
        j = len(word)
        while j > 1 and self.text._get_bbox(word[:j])[2] > width:
            j -= 1
        self.wrapped_line = word[:j]
        if not self.add_line():
            self.reached_end = True
            return
        word = word[j:]
        self.wrapped_line = word
        if self.text._get_bbox(self.wrapped_line)[2] > width:
            self.split_word()


class Text(Generic[AnyStr]):
    def __init__(
        self,
        text: AnyStr,
        font: (
            ImageFont.ImageFont
            | ImageFont.FreeTypeFont
            | ImageFont.TransposedFont
            | None
        ) = None,
        mode: str = "RGB",
        spacing: float = 4,
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
    ) -> None:
        """
        :param text: String to be drawn.
        :param font: Either an :py:class:`~PIL.ImageFont.ImageFont` instance,
                     :py:class:`~PIL.ImageFont.FreeTypeFont` instance,
                     :py:class:`~PIL.ImageFont.TransposedFont` instance or ``None``. If
                     ``None``, the default font from :py:meth:`.ImageFont.load_default`
                     will be used.
        :param mode: The image mode this will be used with.
        :param spacing: The number of pixels between lines.
        :param direction: Direction of the text. It can be ``"rtl"`` (right to left),
                          ``"ltr"`` (left to right) or ``"ttb"`` (top to bottom).
                          Requires libraqm.
        :param features: A list of OpenType font features to be used during text
                         layout. This is usually used to turn on optional font features
                         that are not enabled by default, for example ``"dlig"`` or
                         ``"ss01"``, but can be also used to turn off default font
                         features, for example ``"-liga"`` to disable ligatures or
                         ``"-kern"`` to disable kerning.  To get all supported
                         features, see `OpenType docs`_.
                         Requires libraqm.
        :param language: Language of the text. Different languages may use
                         different glyph shapes or ligatures. This parameter tells
                         the font which language the text is in, and to apply the
                         correct substitutions as appropriate, if available.
                         It should be a `BCP 47 language code`_.
                         Requires libraqm.
        """
        self.text: AnyStr = text
        self.font = font or ImageFont.load_default()

        self.mode = mode
        self.spacing = spacing
        self.direction = direction
        self.features = features
        self.language = language

        self.embedded_color = False

        self.stroke_width: float = 0
        self.stroke_fill: _Ink | None = None

    def embed_color(self) -> None:
        """
        Use embedded color glyphs (COLR, CBDT, SBIX).
        """
        if self.mode not in ("RGB", "RGBA"):
            msg = "Embedded color supported only in RGB and RGBA modes"
            raise ValueError(msg)
        self.embedded_color = True

    def stroke(self, width: float = 0, fill: _Ink | None = None) -> None:
        """
        :param width: The width of the text stroke.
        :param fill: Color to use for the text stroke when drawing. If not given, will
                     default to the ``fill`` parameter from
                     :py:meth:`.ImageDraw.ImageDraw.text`.
        """
        self.stroke_width = width
        self.stroke_fill = fill

    def _get_fontmode(self) -> str:
        if self.mode in ("1", "P", "I", "F"):
            return "1"
        elif self.embedded_color:
            return "RGBA"
        else:
            return "L"

    def wrap(
        self,
        width: int,
        height: int | None = None,
        scaling: str | tuple[str, int] | None = None,
    ) -> Text[AnyStr] | None:
        if not isinstance(self.font, ImageFont.FreeTypeFont):
            msg = "Only FreeTypeFont supported"
            raise ValueError(msg)
        if self.direction not in (None, "ltr"):
            msg = "Only ltr direction supported"
            raise ValueError(msg)

        if scaling is not None:
            if height is None:
                msg = "'scaling' requires 'height'"
                raise ValueError(msg)

        wrap = _Wrap(self, width, height)

        remaining_text = self.text[wrap.remaining_position :]
        if remaining_text:
            text = Text(
                text=remaining_text,
                font=self.font,
                mode=self.mode,
                spacing=self.spacing,
                direction=self.direction,
                features=self.features,
                language=self.language,
            )
            text.embedded_color = self.embedded_color
            text.stroke_width = self.stroke_width
            text.stroke_fill = self.stroke_fill
        else:
            text = None

        if isinstance(self.text, str):
            self.text = "\n".join(cast(list[str], wrap.wrapped_lines))
        else:
            self.text = b"\n".join(cast(list[bytes], wrap.wrapped_lines))
        return text

    def get_length(self) -> float:
        """
        Returns length (in pixels with 1/64 precision) of text.

        This is the amount by which following text should be offset.
        Text bounding box may extend past the length in some fonts,
        e.g. when using italics or accents.

        The result is returned as a float; it is a whole number if using basic layout.

        Note that the sum of two lengths may not equal the length of a concatenated
        string due to kerning. If you need to adjust for kerning, include the following
        character and subtract its length.

        For example, instead of::

            hello = ImageText.Text("Hello", font).get_length()
            world = ImageText.Text("World", font).get_length()
            helloworld = ImageText.Text("HelloWorld", font).get_length()
            assert hello + world == helloworld

        use::

            hello = (
                ImageText.Text("HelloW", font).get_length() -
                ImageText.Text("W", font).get_length()
            )  # adjusted for kerning
            world = ImageText.Text("World", font).get_length()
            helloworld = ImageText.Text("HelloWorld", font).get_length()
            assert hello + world == helloworld

        or disable kerning with (requires libraqm)::

            hello = ImageText.Text("Hello", font, features=["-kern"]).get_length()
            world = ImageText.Text("World", font, features=["-kern"]).get_length()
            helloworld = ImageText.Text(
                "HelloWorld", font, features=["-kern"]
            ).get_length()
            assert hello + world == helloworld

        :return: Either width for horizontal text, or height for vertical text.
        """
        if isinstance(self.text, str):
            multiline = "\n" in self.text
        else:
            multiline = b"\n" in self.text
        if multiline:
            msg = "can't measure length of multiline text"
            raise ValueError(msg)
        return self.font.getlength(
            self.text,
            self._get_fontmode(),
            self.direction,
            self.features,
            self.language,
        )

    def _split(
        self,
        xy: tuple[float, float] = (0, 0),
        anchor: str | None = None,
        align: str = "left",
        lines: list[str] | list[bytes] | None = None,
    ) -> list[_Line]:
        if anchor is None:
            anchor = "lt" if self.direction == "ttb" else "la"
        elif len(anchor) != 2:
            msg = "anchor must be a 2 character string"
            raise ValueError(msg)

        if lines is None:
            lines = (
                self.text.split("\n")
                if isinstance(self.text, str)
                else self.text.split(b"\n")
            )
        if len(lines) == 1:
            return [_Line(xy[0], xy[1], anchor, lines[0])]

        if anchor[1] in "tb" and self.direction != "ttb":
            msg = "anchor not supported for multiline text"
            raise ValueError(msg)

        fontmode = self._get_fontmode()
        line_spacing = (
            self.font.getbbox(
                "A",
                fontmode,
                None,
                self.features,
                self.language,
                self.stroke_width,
            )[3]
            + self.stroke_width
            + self.spacing
        )

        top = xy[1]
        parts = []
        if self.direction == "ttb":
            left = xy[0]
            for line in lines:
                parts.append(_Line(left, top, anchor, line))
                left += line_spacing
        else:
            widths = []
            max_width: float = 0
            for line in lines:
                line_width = self.font.getlength(
                    line, fontmode, self.direction, self.features, self.language
                )
                widths.append(line_width)
                max_width = max(max_width, line_width)

            if anchor[1] == "m":
                top -= (len(lines) - 1) * line_spacing / 2.0
            elif anchor[1] == "d":
                top -= (len(lines) - 1) * line_spacing

            idx = -1
            for line in lines:
                left = xy[0]
                idx += 1
                width_difference = max_width - widths[idx]

                # align by align parameter
                if align in ("left", "justify"):
                    pass
                elif align == "center":
                    left += width_difference / 2.0
                elif align == "right":
                    left += width_difference
                else:
                    msg = 'align must be "left", "center", "right" or "justify"'
                    raise ValueError(msg)

                if (
                    align == "justify"
                    and width_difference != 0
                    and idx != len(lines) - 1
                ):
                    words = (
                        line.split(" ") if isinstance(line, str) else line.split(b" ")
                    )
                    if len(words) > 1:
                        # align left by anchor
                        if anchor[0] == "m":
                            left -= max_width / 2.0
                        elif anchor[0] == "r":
                            left -= max_width

                        word_widths = [
                            self.font.getlength(
                                word,
                                fontmode,
                                self.direction,
                                self.features,
                                self.language,
                            )
                            for word in words
                        ]
                        word_anchor = "l" + anchor[1]
                        width_difference = max_width - sum(word_widths)
                        i = 0
                        for word in words:
                            parts.append(_Line(left, top, word_anchor, word))
                            left += word_widths[i] + width_difference / (len(words) - 1)
                            i += 1
                        top += line_spacing
                        continue

                # align left by anchor
                if anchor[0] == "m":
                    left -= width_difference / 2.0
                elif anchor[0] == "r":
                    left -= width_difference
                parts.append(_Line(left, top, anchor, line))
                top += line_spacing

        return parts

    def _get_bbox(
        self, text: AnyStr, anchor: str | None = None
    ) -> tuple[float, float, float, float]:
        return self.font.getbbox(
            text,
            self._get_fontmode(),
            self.direction,
            self.features,
            self.language,
            self.stroke_width,
        )

    def get_bbox(
        self,
        xy: tuple[float, float] = (0, 0),
        anchor: str | None = None,
        align: str = "left",
    ) -> tuple[float, float, float, float]:
        """
        Returns bounding box (in pixels) of text.

        Use :py:meth:`get_length` to get the offset of following text with 1/64 pixel
        precision. The bounding box includes extra margins for some fonts, e.g. italics
        or accents.

        :param xy: The anchor coordinates of the text.
        :param anchor: The text anchor alignment. Determines the relative location of
                       the anchor to the text. The default alignment is top left,
                       specifically ``la`` for horizontal text and ``lt`` for
                       vertical text. See :ref:`text-anchors` for details.
        :param align: For multiline text, ``"left"``, ``"center"``, ``"right"`` or
                      ``"justify"`` determines the relative alignment of lines. Use the
                      ``anchor`` parameter to specify the alignment to ``xy``.

        :return: ``(left, top, right, bottom)`` bounding box
        """
        bbox: tuple[float, float, float, float] | None = None
        for x, y, anchor, text in self._split(xy, anchor, align):
            bbox_line = self._get_bbox(text, anchor)
            bbox_line = (
                bbox_line[0] + x,
                bbox_line[1] + y,
                bbox_line[2] + x,
                bbox_line[3] + y,
            )
            if bbox is None:
                bbox = bbox_line
            else:
                bbox = (
                    min(bbox[0], bbox_line[0]),
                    min(bbox[1], bbox_line[1]),
                    max(bbox[2], bbox_line[2]),
                    max(bbox[3], bbox_line[3]),
                )

        assert bbox is not None
        return bbox
