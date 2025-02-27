from PIL import Image, ImageSequence, TiffImagePlugin

with open("out.tiff", "w+b") as fp:
    with TiffImagePlugin.AppendingTiffWriter(fp) as tf:
        frame = Image.new("RGB", (100, 100), "#f00")
        frame.encoderconfig = ()
        frame.encoderinfo = {}
        print("_save")
        TiffImagePlugin._save(frame, tf, "out.tiff")
        print("_save end")
        print("closed1" if tf.f.closed else "not closed1")
        tf.newFrame()
        print("closed2" if tf.f.closed else "not closed2")
