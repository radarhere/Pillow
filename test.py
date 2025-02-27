from PIL import TiffImagePlugin

with open("out.tiff", "w+b") as fp:
    with TiffImagePlugin.AppendingTiffWriter(fp) as tf:
        print("closed1" if tf.f.closed else "not closed1")
        tf.newFrame()
        print("closed2" if tf.f.closed else "not closed2")
