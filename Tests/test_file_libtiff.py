from PIL import Image

with Image.open("Tests/images/hopper_lzma.tif") as im:
    im.load()
