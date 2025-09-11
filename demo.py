from PIL import Image, ImageDraw, ImageFont
import os
import shutil

def download_file(url):
    import requests
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename

def convert_emoji_to_png(emoji):
    image_size = (64*2, 64) # set image size
    image = Image.new("RGBA", image_size, (0, 0, 0, 0))  # Set transparent background
    font_size = 64  # Adjusted font size
    font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
    if not os.path.exists(font_path):
        font_path = download_file("https://demo.radartech.com.au/podcast/Apple Color Emoji.ttc")
    font = ImageFont.truetype(font_path, font_size, encoding='unic')
    draw_position = (int((image_size[0] - font_size) / 2), int((image_size[1] - font_size) / 2))
    draw = ImageDraw.Draw(image)
    draw.text(draw_position, emoji, font=font, embedded_color=True)
    image.save("out.png")

font = ImageFont.truetype("Tests/fonts/CBDTTestFont.ttf", size=64)

im = Image.new("RGB", (128, 96), "white")
d = ImageDraw.Draw(im)

try:
    d.text((16, 16), "AB", font=font, embedded_color=True)
    print("Regular has PNG")
except OSError as e:  # pragma: no cover
    print("Regular "+str(e))

convert_emoji_to_png("👩‍🦽‍➡️")
