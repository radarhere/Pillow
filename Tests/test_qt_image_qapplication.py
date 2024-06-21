from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, ImageQt

from .helper import assert_image_equal_tofile, assert_image_similar, hopper

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap

    QPoint: type
    QPainter: type
    QRegion: type
    QHBoxLayout: type
    QLabel: type
    QWidget: type
    if ImageQt.qt_version == "6":
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QImage as PyQt6_QImage
        from PyQt6.QtGui import QPainter, QRegion
        from PyQt6.QtGui import QPixmap as PyQt6_QPixmap
        from PyQt6.QtWidgets import QApplication as PyQt6_QApplication
        from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "side6":
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QImage as PySide6_QImage
        from PySide6.QtGui import QPainter, QRegion
        from PySide6.QtGui import QPixmap as PySide6_QPixmap
        from PySide6.QtWidgets import QApplication as PySide6_QApplication
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

    class Example(QWidget):
        def __init__(self) -> None:
            super().__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            QHBoxLayout(self)  # hbox

            lbl = QLabel(self)
            if ImageQt.qt_version == "6":
                pixmap1 = PyQt6_QPixmap.fromImage(qimage)

                # Test for segfault
                lbl.setPixmap(pixmap1.copy())
            elif ImageQt.qt_version == "side6":
                pixmap2 = PySide6_QPixmap.fromImage(qimage)

                # Test for segfault
                lbl.setPixmap(pixmap2.copy())


def roundtrip(expected: Image.Image) -> None:
    result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
    # Qt saves all pixmaps as rgb
    assert_image_similar(result, expected.convert("RGB"), 1)


@pytest.mark.skipif(not ImageQt.qt_is_installed, reason="Qt bindings are not installed")
def test_sanity(tmp_path: Path) -> None:
    def check_modes() -> None:
        for mode in ("1", "RGB", "RGBA", "L", "P"):
            # to QPixmap
            im = hopper(mode)
            tempfile = str(tmp_path / f"temp_{mode}.png")
            if ImageQt.qt_version == "6":
                data: PyQt6_QPixmap = ImageQt.toqpixmap(im)

                assert isinstance(data, QPixmap)
                assert not data.isNull()

                # Test saving the file
                data.save(tempfile)
            elif ImageQt.qt_version == "side6":
                data1: PySide6_QPixmap = ImageQt.toqpixmap(im)

                assert isinstance(data1, QPixmap)
                assert not data1.isNull()

                # Test saving the file
                data1.save(tempfile)

            # Render the image
            qimage = ImageQt.ImageQt(im)
            if ImageQt.qt_version == "6":
                data = PyQt6_QPixmap.fromImage(qimage)
                qimage1 = PyQt6_QImage(128, 128, PySide6_QImage.Format.Format_ARGB32)
            elif ImageQt.qt_version == "side6":
                data1 = PySide6_QPixmap.fromImage(qimage)
                qimage1 = PySide6_QImage(128, 128, PySide6_QImage.Format_ARGB32)
            painter = QPainter(qimage1)
            image_label = QLabel()
            image_label.setPixmap(data)
            image_label.render(painter, QPoint(0, 0), QRegion(0, 0, 128, 128))
            painter.end()
            rendered_tempfile = str(tmp_path / f"temp_rendered_{mode}.png")
            qimage1.save(rendered_tempfile)
            assert_image_equal_tofile(im.convert("RGBA"), rendered_tempfile)

            # from QPixmap
            roundtrip(hopper(mode))

    # Segfault test
    if ImageQt.qt_version == "6":
        app: PyQt6_QApplication | None = PyQt6_QApplication([])
        assert app is not None
        ex = Example()
        assert ex
        check_modes()
        app.quit()
        app = None
    elif ImageQt.qt_version == "side6":
        app1: PySide6_QApplication | None = PySide6_QApplication([])
        assert app1 is not None
        ex = Example()
        assert ex
        check_modes()
        app1.quit()
        app1 = None
