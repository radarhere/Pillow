from __future__ import annotations

import os
import subprocess
import sys
import sysconfig

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper, is_win32

TYPE_CHECKING = False
if TYPE_CHECKING:
    from types import ModuleType


class TestEmbeddable:
    @pytest.mark.xfail(not (sys.version_info >= (3, 13)), reason="failing test")
    @pytest.mark.skipif(not is_win32(), reason="requires Windows")
    def test_embeddable(self) -> None:
        pytest.importorskip("setuptools", reason="setuptools not installed")
        import ctypes

        from setuptools.command import build_ext

        compiler = getattr(build_ext, "new_compiler")()
        compiler.add_include_dir(sysconfig.get_config_var("INCLUDEPY"))
        print("torch", sysconfig.get_config_var("INCLUDEPY"))

        libdir = sysconfig.get_config_var("LIBDIR") or sysconfig.get_config_var(
            "INCLUDEPY"
        ).replace("include", "libs")
        compiler.add_library_dir(libdir)
        try:
            compiler.initialize()
        except Exception:
            pytest.skip("Compiler could not be initialized")

        with open("embed_pil.c", "w", encoding="utf-8") as fh:
            home = sys.prefix.replace("\\", "\\\\")
            fh.write(f"""
#include <Python.h>

int main(int argc, char* argv[])
{{
    char *home = "{home}";
    wchar_t *whome = Py_DecodeLocale(home, NULL);
    PyConfig config;
    PyConfig_InitPythonConfig(&config);
    config.home = whome;

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    PyMem_RawFree(whome);
    PyConfig_Clear(&config);

    return 0;
}}
        """)

        objects = compiler.compile(["embed_pil.c"])
        compiler.link_executable(objects, "embed_pil")

        env = os.environ.copy()
        env["PATH"] = sys.prefix + ";" + env["PATH"]

        # Do not display the Windows Error Reporting dialog
        getattr(ctypes, "windll").kernel32.SetErrorMode(0x0002)

        process = subprocess.Popen(["embed_pil.exe"], env=env)
        process.communicate()
        assert process.returncode == 0

    def teardown_method(self) -> None:
        try:
            os.remove("embed_pil.c")
        except FileNotFoundError:
            # If the test was skipped or failed, the file won't exist
            pass
