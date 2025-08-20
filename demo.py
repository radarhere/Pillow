# pyright: strict

from PIL import Image

img = Image.new('RGB', (10, 10))
data = img.getdata()
reveal_type(data)
