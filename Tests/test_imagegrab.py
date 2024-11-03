from __future__ import annotations

import os
import shutil
import subprocess
import sys
import win32gui

import pytest

from PIL import Image, ImageGrab

from .helper import assert_image_equal_tofile, skip_unless_feature


def callback(hwnd, strings):
    strings.append(win32gui.GetWindowText(hwnd))
    return True

class TestImageGrab:
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_grab_handle(self):
        win_list = []  # list of strings containing win handles and window titles
        win32gui.EnumWindows(callback, win_list)  # populate list
        print(win_list)

        x = win32gui.FindWindow(None, "Administrator: C:\\actions\\runner-provisioner-Windows\\provisioner.exe")
        print("findwindow", x)
        ImageGrab.grab(handle=x).save("out.png")
