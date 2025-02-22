# > pyroma .
# ------------------------------
# Checking .
# Found Pillow
# ------------------------------
# Final rating: 10/10
# Your cheese is so fresh most people think it's a cream: Mascarpone
# ------------------------------
from __future__ import annotations

import os
import re
import shutil
import struct
import subprocess
import sys
import warnings
from collections.abc import Iterator
from typing import Any

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


def get_version() -> str:
    version_file = "src/PIL/_version.py"
    with open(version_file, encoding="utf-8") as f:
        return f.read().split('"')[1]


configuration: dict[str, list[str]] = {}


PILLOW_VERSION = get_version()
FREETYPE_ROOT = None
HARFBUZZ_ROOT = None
FRIBIDI_ROOT = None
IMAGEQUANT_ROOT = None
JPEG2K_ROOT = None
JPEG_ROOT = None
LCMS_ROOT = None
RAQM_ROOT = None
TIFF_ROOT = None
WEBP_ROOT = None
ZLIB_ROOT = None
FUZZING_BUILD = "LIB_FUZZING_ENGINE" in os.environ

if sys.platform == "win32" and sys.version_info >= (3, 14):
    import atexit

    atexit.register(
        lambda: warnings.warn(
            f"Pillow {PILLOW_VERSION} does not support Python "
            f"{sys.version_info.major}.{sys.version_info.minor} and does not provide "
            "prebuilt Windows binaries. We do not recommend building from source on "
            "Windows.",
            RuntimeWarning,
        )
    )


_IMAGING = ("decode", "encode", "map", "display", "outline", "path")

_LIB_IMAGING = (
    "Access",
    "AlphaComposite",
    "Resample",
    "Reduce",
    "Bands",
    "BcnDecode",
    "BitDecode",
    "Blend",
    "Chops",
    "ColorLUT",
    "Convert",
    "ConvertYCbCr",
    "Copy",
    "Crop",
    "Dib",
    "Draw",
    "Effects",
    "EpsEncode",
    "File",
    "Fill",
    "Filter",
    "FliDecode",
    "Geometry",
    "GetBBox",
    "GifDecode",
    "GifEncode",
    "HexDecode",
    "Histo",
    "JpegDecode",
    "JpegEncode",
    "Matrix",
    "ModeFilter",
    "Negative",
    "Offset",
    "Pack",
    "PackDecode",
    "Palette",
    "Paste",
    "Quant",
    "QuantOctree",
    "QuantHash",
    "QuantHeap",
    "PcdDecode",
    "PcxDecode",
    "PcxEncode",
    "Point",
    "RankFilter",
    "RawDecode",
    "RawEncode",
    "Storage",
    "SgiRleDecode",
    "SunRleDecode",
    "TgaRleDecode",
    "TgaRleEncode",
    "Unpack",
    "UnpackYCC",
    "UnsharpMask",
    "XbmDecode",
    "XbmEncode",
    "ZipDecode",
    "ZipEncode",
    "TiffDecode",
    "Jpeg2KDecode",
    "Jpeg2KEncode",
    "BoxBlur",
    "QuantPngQuant",
    "codec_fd",
)

DEBUG = False


class DependencyException(Exception):
    pass


class RequiredDependencyException(Exception):
    pass


PLATFORM_MINGW = os.name == "nt" and "GCC" in sys.version


def _dbg(s: str, tp: Any = None) -> None:
    if DEBUG:
        if tp:
            print(s % tp)
            return
        print(s)


def _find_library_dirs_ldconfig() -> list[str]:
    # Based on ctypes.util from Python 2

    ldconfig = "ldconfig" if shutil.which("ldconfig") else "/sbin/ldconfig"
    args: list[str]
    env: dict[str, str]
    expr: str
    if sys.platform.startswith("linux") or sys.platform.startswith("gnu"):
        if struct.calcsize("l") == 4:
            machine = os.uname()[4] + "-32"
        else:
            machine = os.uname()[4] + "-64"
        mach_map = {
            "x86_64-64": "libc6,x86-64",
            "ppc64-64": "libc6,64bit",
            "sparc64-64": "libc6,64bit",
            "s390x-64": "libc6,64bit",
            "ia64-64": "libc6,IA-64",
        }
        abi_type = mach_map.get(machine, "libc6")

        # Assuming GLIBC's ldconfig (with option -p)
        # Alpine Linux uses musl that can't print cache
        args = [ldconfig, "-p"]
        expr = rf".*\({abi_type}.*\) => (.*)"
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["LANG"] = "C"

    elif sys.platform.startswith("freebsd"):
        args = [ldconfig, "-r"]
        expr = r".* => (.*)"
        env = {}

    try:
        p = subprocess.Popen(
            args, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env, text=True
        )
    except OSError:  # E.g. command not found
        return []
    data = p.communicate()[0]

    dirs = []
    for dll in re.findall(expr, data):
        dir = os.path.dirname(dll)
        if dir not in dirs:
            dirs.append(dir)
    return dirs


def _add_directory(
    path: list[str], subdir: str | None, where: int | None = None
) -> None:
    if subdir is None:
        return
    subdir = os.path.realpath(subdir)
    if os.path.isdir(subdir) and subdir not in path:
        if where is None:
            _dbg("Appending path %s", subdir)
            path.append(subdir)
        else:
            _dbg("Inserting path %s", subdir)
            path.insert(where, subdir)
    elif subdir in path and where is not None:
        path.remove(subdir)
        path.insert(where, subdir)


def _find_include_file(self: pil_build_ext, include: str) -> int:
    for directory in self.compiler.include_dirs:
        _dbg("Checking for include file %s in %s", (include, directory))
        if os.path.isfile(os.path.join(directory, include)):
            _dbg("Found %s", include)
            return 1
    return 0


def _find_library_file(self: pil_build_ext, library: str) -> str | None:
    ret = self.compiler.find_library_file(self.compiler.library_dirs, library)
    if ret:
        _dbg("Found library %s at %s", (library, ret))
    else:
        _dbg("Couldn't find library %s in %s", (library, self.compiler.library_dirs))
    return ret


def _find_include_dir(self: pil_build_ext, dirname: str, include: str) -> bool | str:
    for directory in self.compiler.include_dirs:
        _dbg("Checking for include file %s in %s", (include, directory))
        if os.path.isfile(os.path.join(directory, include)):
            _dbg("Found %s in %s", (include, directory))
            return True
        subdir = os.path.join(directory, dirname)
        _dbg("Checking for include file %s in %s", (include, subdir))
        if os.path.isfile(os.path.join(subdir, include)):
            _dbg("Found %s in %s", (include, subdir))
            return subdir
    return False


def _cmd_exists(cmd: str) -> bool:
    if "PATH" not in os.environ:
        return False
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


def _pkg_config(name: str) -> tuple[list[str], list[str]] | None:
    command = os.environ.get("PKG_CONFIG", "pkg-config")
    for keep_system in (True, False):
        try:
            command_libs = [command, "--libs-only-L", name]
            command_cflags = [command, "--cflags-only-I", name]
            stderr = None
            if keep_system:
                command_libs.append("--keep-system-libs")
                command_cflags.append("--keep-system-cflags")
                stderr = subprocess.DEVNULL
            if not DEBUG:
                command_libs.append("--silence-errors")
                command_cflags.append("--silence-errors")
            libs = re.split(
                r"(^|\s+)-L",
                subprocess.check_output(command_libs, stderr=stderr)
                .decode("utf8")
                .strip(),
            )[::2][1:]
            cflags = re.split(
                r"(^|\s+)-I",
                subprocess.check_output(command_cflags).decode("utf8").strip(),
            )[::2][1:]
            return libs, cflags
        except Exception:
            pass
    return None


class pil_build_ext(build_ext):
    class ext_feature:
        features = [
            "zlib",
            "jpeg",
        ]

        required = {"jpeg", "zlib"}
        vendor: set[str] = set()

        def __init__(self) -> None:
            self._settings: dict[str, str | bool | None] = {}
            for f in self.features:
                self.set(f, None)

        def require(self, feat: str) -> bool:
            return feat in self.required

        def get(self, feat: str) -> str | bool | None:
            return self._settings[feat]

        def set(self, feat: str, value: str | bool | None) -> None:
            self._settings[feat] = value

        def want(self, feat: str) -> bool:
            return self._settings[feat] is None

        def want_vendor(self, feat: str) -> bool:
            return feat in self.vendor

        def __iter__(self) -> Iterator[str]:
            yield from self.features

    feature = ext_feature()

    user_options = (
        build_ext.user_options
        + [(f"disable-{x}", None, f"Disable support for {x}") for x in feature]
        + [(f"enable-{x}", None, f"Enable support for {x}") for x in feature]
        + [
            (f"vendor-{x}", None, f"Use vendored version of {x}")
            for x in ("raqm", "fribidi")
        ]
        + [
            ("disable-platform-guessing", None, "Disable platform guessing"),
            ("debug", None, "Debug logging"),
        ]
        + [("add-imaging-libs=", None, "Add libs to _imaging build")]
    )

    @staticmethod
    def check_configuration(option: str, value: str) -> bool | None:
        return True if value in configuration.get(option, []) else None

    def initialize_options(self) -> None:
        self.disable_platform_guessing = self.check_configuration(
            "platform-guessing", "disable"
        )
        self.add_imaging_libs = ""
        build_ext.initialize_options(self)
        for x in self.feature:
            setattr(self, f"disable_{x}", self.check_configuration(x, "disable"))
            setattr(self, f"enable_{x}", self.check_configuration(x, "enable"))
        for x in ("raqm", "fribidi"):
            setattr(self, f"vendor_{x}", self.check_configuration(x, "vendor"))
        if self.check_configuration("debug", "true"):
            self.debug = True
        self.parallel = configuration.get("parallel", [None])[-1]

    def finalize_options(self) -> None:
        build_ext.finalize_options(self)
        if self.debug:
            global DEBUG
            DEBUG = True
        if not self.parallel:
            # If --parallel (or -j) wasn't specified, we want to reproduce the same
            # behavior as before, that is, auto-detect the number of jobs.
            self.parallel = None

            cpu_count = os.cpu_count()
            if cpu_count is not None:
                try:
                    self.parallel = int(
                        os.environ.get("MAX_CONCURRENCY", min(4, cpu_count))
                    )
                except TypeError:
                    pass
        for x in self.feature:
            if getattr(self, f"disable_{x}"):
                self.feature.set(x, False)
                self.feature.required.discard(x)
                _dbg("Disabling %s", x)
                if getattr(self, f"enable_{x}"):
                    msg = f"Conflicting options: '-C {x}=enable' and '-C {x}=disable'"
                    raise ValueError(msg)
                if x == "freetype":
                    _dbg("'-C freetype=disable' implies '-C raqm=disable'")
                    if getattr(self, "enable_raqm"):
                        msg = (
                            "Conflicting options: "
                            "'-C raqm=enable' and '-C freetype=disable'"
                        )
                        raise ValueError(msg)
                    setattr(self, "disable_raqm", True)
            if getattr(self, f"enable_{x}"):
                _dbg("Requiring %s", x)
                self.feature.required.add(x)
                if x == "raqm":
                    _dbg("'-C raqm=enable' implies '-C freetype=enable'")
                    self.feature.required.add("freetype")
        for x in ("raqm", "fribidi"):
            if getattr(self, f"vendor_{x}"):
                if getattr(self, "disable_raqm"):
                    msg = f"Conflicting options: '-C {x}=vendor' and '-C raqm=disable'"
                    raise ValueError(msg)
                if x == "fribidi" and not getattr(self, "vendor_raqm"):
                    msg = (
                        f"Conflicting options: '-C {x}=vendor' and not '-C raqm=vendor'"
                    )
                    raise ValueError(msg)
                _dbg("Using vendored version of %s", x)
                self.feature.vendor.add(x)

    def _update_extension(
        self,
        name: str,
        libraries: list[str] | list[str | bool | None],
        define_macros: list[tuple[str, str | None]] | None = None,
        sources: list[str] | None = None,
    ) -> None:
        for extension in self.extensions:
            if extension.name == name:
                extension.libraries += libraries
                if define_macros is not None:
                    extension.define_macros += define_macros
                if sources is not None:
                    extension.sources += sources
                if FUZZING_BUILD:
                    extension.language = "c++"
                    extension.extra_link_args = ["--stdlib=libc++"]
                break

    def _remove_extension(self, name: str) -> None:
        for extension in self.extensions:
            if extension.name == name:
                self.extensions.remove(extension)
                break

    def get_macos_sdk_path(self) -> str | None:
        try:
            sdk_path = (
                subprocess.check_output(["xcrun", "--show-sdk-path", "--sdk", "macosx"])
                .strip()
                .decode("latin1")
            )
        except Exception:
            sdk_path = None
        if (
            not sdk_path
            or sdk_path == "/Applications/Xcode.app/Contents/Developer"
            "/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
        ):
            commandlinetools_sdk_path = (
                "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
            )
            if os.path.exists(commandlinetools_sdk_path):
                sdk_path = commandlinetools_sdk_path
        return sdk_path

    def build_extensions(self) -> None:
        library_dirs: list[str] = []
        include_dirs: list[str] = []

        pkg_config = None
        if _cmd_exists(os.environ.get("PKG_CONFIG", "pkg-config")):
            pkg_config = _pkg_config

        #
        # add configured kits
        for root_name, lib_name in {
            "JPEG_ROOT": "libjpeg",
            "ZLIB_ROOT": "zlib",
        }.items():
            root = globals()[root_name]

            if root is None and root_name in os.environ:
                root_prefix = os.environ[root_name]
                root = (
                    os.path.join(root_prefix, "lib"),
                    os.path.join(root_prefix, "include"),
                )

            if root is None and pkg_config:
                if isinstance(lib_name, str):
                    _dbg(f"Looking for `{lib_name}` using pkg-config.")
                    root = pkg_config(lib_name)
                else:
                    for lib_name2 in lib_name:
                        _dbg(f"Looking for `{lib_name2}` using pkg-config.")
                        root = pkg_config(lib_name2)
                        if root:
                            break

            if isinstance(root, tuple):
                lib_root, include_root = root
            else:
                lib_root = include_root = root

            if lib_root is not None:
                if not isinstance(lib_root, (tuple, list)):
                    lib_root = (lib_root,)
                for lib_dir in lib_root:
                    _add_directory(library_dirs, lib_dir)
            if include_root is not None:
                if not isinstance(include_root, (tuple, list)):
                    include_root = (include_root,)
                for include_dir in include_root:
                    _add_directory(include_dirs, include_dir)

        # respect CFLAGS/CPPFLAGS/LDFLAGS
        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in os.environ:
                for match in re.finditer(r"-I([^\s]+)", os.environ[k]):
                    _add_directory(include_dirs, match.group(1))
                for match in re.finditer(r"-L([^\s]+)", os.environ[k]):
                    _add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables:
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(library_dirs, d)

        _add_directory(library_dirs, os.path.join(sys.prefix, "lib"))
        _add_directory(include_dirs, os.path.join(sys.prefix, "include"))

        #
        # add platform directories

        if self.disable_platform_guessing:
            pass

        elif sys.platform == "darwin":
            # attempt to make sure we pick freetype2 over other versions
            _add_directory(include_dirs, "/sw/include/freetype2")
            _add_directory(include_dirs, "/sw/lib/freetype2/include")
            # fink installation directories
            _add_directory(library_dirs, "/sw/lib")
            _add_directory(include_dirs, "/sw/include")
            # darwin ports installation directories
            _add_directory(library_dirs, "/opt/local/lib")
            _add_directory(include_dirs, "/opt/local/include")

            # if Homebrew is installed, use its lib and include directories
            try:
                prefix = (
                    subprocess.check_output(["brew", "--prefix"])
                    .strip()
                    .decode("latin1")
                )
            except Exception:
                # Homebrew not installed
                prefix = None

            ft_prefix = None

            if prefix:
                # add Homebrew's include and lib directories
                _add_directory(library_dirs, os.path.join(prefix, "lib"))
                _add_directory(include_dirs, os.path.join(prefix, "include"))
                _add_directory(
                    include_dirs, os.path.join(prefix, "opt", "zlib", "include")
                )
                ft_prefix = os.path.join(prefix, "opt", "freetype")

            if ft_prefix and os.path.isdir(ft_prefix):
                # freetype might not be linked into Homebrew's prefix
                _add_directory(library_dirs, os.path.join(ft_prefix, "lib"))
                _add_directory(include_dirs, os.path.join(ft_prefix, "include"))
            else:
                # fall back to freetype from XQuartz if
                # Homebrew's freetype is missing
                _add_directory(library_dirs, "/usr/X11/lib")
                _add_directory(include_dirs, "/usr/X11/include")

            # Add the macOS SDK path.
            sdk_path = self.get_macos_sdk_path()
            if sdk_path:
                _add_directory(library_dirs, os.path.join(sdk_path, "usr", "lib"))
                _add_directory(include_dirs, os.path.join(sdk_path, "usr", "include"))

                for extension in self.extensions:
                    extension.extra_compile_args = ["-Wno-nullability-completeness"]

        # FIXME: check /opt/stuff directories here?

        # standard locations
        if not self.disable_platform_guessing:
            _add_directory(library_dirs, "/usr/local/lib")
            _add_directory(include_dirs, "/usr/local/include")

            _add_directory(library_dirs, "/usr/lib")
            _add_directory(include_dirs, "/usr/include")
            # alpine, at least
            _add_directory(library_dirs, "/lib")

        #
        # insert new dirs *before* default libs, to avoid conflicts
        # between Python PYD stub libs and real libraries

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        #
        # look for available libraries

        feature = self.feature

        if feature.want("zlib"):
            _dbg("Looking for zlib")
            if _find_include_file(self, "zlib.h"):
                if _find_library_file(self, "z"):
                    feature.set("zlib", "z")
                elif sys.platform == "win32" and _find_library_file(self, "zlib"):
                    feature.set("zlib", "zlib")  # alternative name
                elif sys.platform == "win32" and _find_library_file(self, "zdll"):
                    feature.set("zlib", "zdll")  # dll import library

        if feature.want("jpeg"):
            _dbg("Looking for jpeg")
            if _find_include_file(self, "jpeglib.h"):
                if _find_library_file(self, "jpeg"):
                    feature.set("jpeg", "jpeg")
                elif sys.platform == "win32" and _find_library_file(self, "libjpeg"):
                    feature.set("jpeg", "libjpeg")  # alternative name

        for f in feature:
            if not feature.get(f) and feature.require(f):
                if f in ("jpeg", "zlib"):
                    raise RequiredDependencyException(f)
                raise DependencyException(f)

        #
        # core library

        libs: list[str | bool | None] = []
        libs.extend(self.add_imaging_libs.split())
        defs: list[tuple[str, str | None]] = []
        if feature.get("jpeg"):
            libs.append(feature.get("jpeg"))
            defs.append(("HAVE_LIBJPEG", None))
        if feature.get("zlib"):
            libs.append(feature.get("zlib"))
            defs.append(("HAVE_LIBZ", None))
        if struct.unpack("h", b"\0\1")[0] == 1:
            defs.append(("WORDS_BIGENDIAN", None))

        defs.append(("PILLOW_VERSION", f'"{PILLOW_VERSION}"'))

        self._update_extension("PIL._imaging", libs, defs)

        tk_libs = ["psapi"] if sys.platform in ("win32", "cygwin") else []
        self._update_extension("PIL._imagingtk", tk_libs)

        build_ext.build_extensions(self)


def debug_build() -> bool:
    return hasattr(sys, "gettotalrefcount") or FUZZING_BUILD


files: list[str | os.PathLike[str]] = ["src/_imaging.c"]
for src_file in _IMAGING:
    files.append("src/" + src_file + ".c")
for src_file in _LIB_IMAGING:
    files.append(os.path.join("src/libImaging", src_file + ".c"))
ext_modules = [
    Extension("PIL._imaging", files)
]


# parse configuration from _custom_build/backend.py
while sys.argv[-1].startswith("--pillow-configuration="):
    _, key, value = sys.argv.pop().split("=", 2)
    configuration.setdefault(key, []).append(value)

try:
    setup(
        cmdclass={"build_ext": pil_build_ext},
        ext_modules=ext_modules,
        zip_safe=not (debug_build() or PLATFORM_MINGW),
    )
except RequiredDependencyException as err:
    msg = f"""

The headers or library files could not be found for {str(err)},
a required dependency when compiling Pillow from source.

Please see the install instructions at:
   https://pillow.readthedocs.io/en/latest/installation/basic-installation.html

"""
    sys.stderr.write(msg)
    raise RequiredDependencyException(msg)
except DependencyException as err:
    msg = f"""

The headers or library files could not be found for {str(err)},
which was requested by the option flag '-C {str(err)}=enable'

"""
    sys.stderr.write(msg)
    raise DependencyException(msg)
