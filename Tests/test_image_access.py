from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
from types import ModuleType

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper, is_win32

numpy: ModuleType | None
try:
    import numpy
except ImportError:
    numpy = None



class TestEmbeddable:
    @pytest.mark.skipif(not is_win32(), reason="requires Windows")
    def test_embeddable(self) -> None:
        import platform
        print("torch", platform.machine())
        assert False
        import ctypes

        from setuptools.command import build_ext

        with open("embed_pil.c", "w", encoding="utf-8") as fh:
            home = sys.prefix.replace("\\", "\\\\")
            fh.write(
                f"""
#include "Python.h"

int main(int argc, char* argv[])
{{
    char *home = "{home}";
    wchar_t *whome = Py_DecodeLocale(home, NULL);
    Py_SetPythonHome(whome);

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    PyMem_RawFree(whome);

    return 0;
}}
        """
            )

        compiler = getattr(build_ext, "new_compiler")()
        compiler.add_include_dir(sysconfig.get_config_var("INCLUDEPY"))

        libdir = sysconfig.get_config_var("LIBDIR") or sysconfig.get_config_var(
            "INCLUDEPY"
        ).replace("include", "libs")
        compiler.add_library_dir(libdir)
        objects = compiler.compile(["embed_pil.c"])
        compiler.link_executable(objects, "embed_pil")

        env = os.environ.copy()
        env["PATH"] = sys.prefix + ";" + env["PATH"]

        # Do not display the Windows Error Reporting dialog
        getattr(ctypes, "windll").kernel32.SetErrorMode(0x0002)

        process = subprocess.Popen(["embed_pil.exe"], env=env)
        process.communicate()
        assert process.returncode == 0
