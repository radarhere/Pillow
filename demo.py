from io import BytesIO
from PIL import Image
with Image.open("Tests/images/avif/hopper.avif") as im:
    test_buf = BytesIO()
    print()
    im.save(test_buf, "AVIF")
    ctrl_buf = BytesIO()
    im.save(ctrl_buf, "AVIF", advanced=0)
    if ctrl_buf.getvalue() == test_buf.getvalue():
        print("The default save and enable-chroma-deltaq=0 save match, so enable-chroma-deltaq=0 is the default behaviour")
    else:
        ctrl_buf1 = BytesIO()
        im.save(ctrl_buf1, "AVIF", advanced=1)
        if ctrl_buf1.getvalue() == test_buf.getvalue():
            print("The default save and enable-chroma-deltaq=0 save do not match. Instead enable-chroma-deltaq=1 is the default behaviour")
        else:
            print("The default save and enable-chroma-deltaq=0 save do not match")
        print()
        assert False
