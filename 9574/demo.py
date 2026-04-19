from __future__ import annotations

from PIL import Image

im = Image.open("../Tests/images/m13.fits")
maxi = 0
mini = 10000000000000
for x in range(im.width):
    for y in range(im.width):
        v = im.load()[x, y]
        if v < 0:
            print(v)
        if v < mini:
            mini = v
        if v > maxi:
            maxi = v
print("max", maxi, "min", mini)
# im.save("out.png")
