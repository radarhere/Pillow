from __future__ import annotations

import numpy
from matplotlib import pyplot as plt

import PIL.Image

filename = "../Tests/images/m13.fits"
arr = numpy.asarray(PIL.Image.open(filename))
arr = arr.byteswap()  # workaround to correct Big Endian byte order
plt.imshow(arr, cmap="gray")
plt.show()
