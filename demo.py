import tempfile
import threading
from PIL import Image

def test():
    with Image.open("3-pages.tiff") as im, tempfile.NamedTemporaryFile('wb') as f:
        im.save(f, format="TIFF", compression="tiff_lzw")

threads = []

for i in range(256):
    t = threading.Thread(target=test, daemon=True)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
