import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

try:
    import tkinter as tk

    from PIL import ImageTk

    dir(ImageTk)
    HAS_TK = True
except (OSError, ImportError):
    # Skipped via pytestmark
    HAS_TK = False


pytestmark = pytest.mark.skipif(not HAS_TK, reason="Tk not installed")


def setup_module():
    try:
        # setup tk
        tk.Frame()
        # root = tk.Tk()
    except tk.TclError as v:
        pytest.skip(f"TCL Error: {v}")


def test_photoimage():
    im = hopper("1")

    # this should not crash
    im_tk = ImageTk.PhotoImage(im)

