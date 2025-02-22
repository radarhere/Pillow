from __future__ import annotations

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class pil_build_ext(build_ext):
    def build_extensions(self) -> None:
        self.compiler.library_dirs = ["/Users/runner/work/Pillow/Pillow/build/deps/darwin/lib"] + self.compiler.library_dirs
        self.compiler.include_dirs = ["/Users/runner/work/Pillow/Pillow/build/deps/darwin/include"] + self.compiler.include_dirs

        self.extensions[0].libraries += ["z"]

        build_ext.build_extensions(self)


setup(
    cmdclass={"build_ext": pil_build_ext},
    ext_modules=[
        Extension("PIL._imaging", ["src/_imaging.c"]),
    ],
    zip_safe=True,
)
