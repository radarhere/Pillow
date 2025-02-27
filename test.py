from PIL import Image, ImageSequence, TiffImagePlugin

# Preparation
import numpy as np
images = [np.asarray(im) for im in [
    Image.new("RGB", (100, 100), "#f00"),
    Image.new("RGB", (100, 100), "#0f0")
]]
listOfTuples = [
    (55, [1, 3]),
    (56, [2, 4])
]

# Script
image_list = []
for image in images:
    image_list.append(Image.fromarray(image))
frames = []
for i, frame in enumerate(image_list):
    info = TiffImagePlugin.ImageFileDirectory()

    for tupleIdTag, tupleTags in listOfTuples:
        info[tupleIdTag] = tupleTags[i]
        info.tagtype[tupleIdTag] = 3

    frame.encoderinfo = {'tiffinfo': info}
    frames.append(frame)
with open("out.tiff", "w+b") as fp:
    with TiffImagePlugin.AppendingTiffWriter(fp) as tf:
        frame = frames[0]
        frame.encoderconfig = ()
        print("_save", i)
        TiffImagePlugin._save(frame, tf, "out.tiff")
        print("_save end", i)
