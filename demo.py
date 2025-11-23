from pathlib import Path
import hashlib
import math
import platform

from PIL import Image, ImageDraw, ImageFont

FONT_SIZE = 20  # in pixels
H_SPACING = 20  # in pixels
V_SPACING = 80  # in pixels
OPACITY = 70  # 0-255
TEXT = "Watermark"
ROOT_PATH = Path(__file__).parent.parent.absolute()


def main() -> None:
    font_path = "Roboto-Regular.ttf"
    font = ImageFont.truetype(font=font_path, size=FONT_SIZE)
    image = Image.new(mode="RGB", size=(600, 600), color=(0, 0, 0))
    image_width, image_height = image.size

    draw = ImageDraw.Draw(im=image)
    _, _, text_width, text_height = draw.textbbox(xy=(0, 0), text=TEXT, font=font)
    text_width = math.ceil(text_width)
    text_height = math.ceil(text_height)

    image_text = Image.new(mode="RGBA", size=(text_width, text_height))
    draw = ImageDraw.Draw(im=image_text)
    draw.text(
        xy=(0, 0),
        text=TEXT,
        fill=(255, 255, 255, OPACITY),
        font=font,
    )
    image_text = image_text.rotate(
        angle=45, expand=True, resample=Image.Resampling.BICUBIC
    )

    current_width = 0
    current_height = 0
    new_position = (current_width, current_height)

    up_down = 1
    while current_width < image_width:
        image.paste(im=image_text, box=new_position, mask=image_text)

        repeat_current_width, repeat_current_height = new_position
        while repeat_current_height < image_height:
            repeat_new_position = (
                repeat_current_width,
                repeat_current_height + text_height + V_SPACING,
            )
            image.paste(im=image_text, box=repeat_new_position, mask=image_text)
            repeat_current_width, repeat_current_height = repeat_new_position

        up_down *= -1
        new_position = (
            current_width + text_width + H_SPACING,
            current_height + up_down * V_SPACING // 2,
        )
        current_width, current_height = new_position

    image.save(fp="out.png")
    with open("out.png", "rb") as fp:
        print("digest", hashlib.sha256(fp.read()).hexdigest())


if __name__ == "__main__":
    main()
