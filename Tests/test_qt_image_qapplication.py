import pytest

from PIL import ImageQt

from .helper import assert_image_equal, hopper

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap

    if ImageQt.qt_version == "side6":
        from PySide6 import QtGui
        from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "5":
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "side2":
        from PySide2 import QtGui
        from PySide2.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

    app = QApplication([])

    class Example(QWidget):
        def __init__(self):
            super().__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = QtGui.QPixmap.fromImage(qimage)

            QHBoxLayout(self)  # hbox

            lbl = QLabel(self)
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())


def roundtrip(expected):
    result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
    # Qt saves all pixmaps as rgb
    assert_image_equal(result, expected.convert("RGB"))


@pytest.mark.skipif(not ImageQt.qt_is_installed, reason="Qt bindings are not installed")
def test_sanity(tmp_path):
    # Segfault test
    ex = Example()
    assert app  # Silence warning
    assert ex  # Silence warning

    # class TestFromQPixmap(PillowQPixmapTestCase):
    for mode in ("1", "RGB", "RGBA", "L", "P"):
        roundtrip(hopper(mode))

    # class TestToQPixmap(PillowQPixmapTestCase):
    for mode in ("1", "RGB", "RGBA", "L", "P"):
        data = ImageQt.toqpixmap(hopper(mode))

        assert isinstance(data, QPixmap)
        assert not data.isNull()

        # Test saving the file
        tempfile = str(tmp_path / f"temp_{mode}.png")
        data.save(tempfile)

    app.quit()
    app = None
