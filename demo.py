import importlib.metadata
from PIL import Image, ImageDraw

version = importlib.metadata.version("Pillow")
print(f"{version=}")

size = (16, 16)
im = Image.new("RGB", size, "black")
draw = ImageDraw.Draw(im)
draw.ellipse((0, 0, size[0] - 1, size[1] - 1), fill="red")

im.save(f"im-{version}.png", format="PNG")
