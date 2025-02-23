#!/bin/bash

# Setup that needs to be done before multibuild utils are invoked
PROJECTDIR=$(pwd)
if [[ "$(uname -s)" == "Darwin" ]]; then
    # Safety check - macOS builds require that CIBW_ARCHS is set, and that it
    # only contains a single value (even though cibuildwheel allows multiple
    # values in CIBW_ARCHS).
    if [[ -z "$CIBW_ARCHS" ]]; then
        echo "ERROR: Pillow macOS builds require CIBW_ARCHS be defined."
        exit 1
    fi
    if [[ "$CIBW_ARCHS" == *" "* ]]; then
        echo "ERROR: Pillow macOS builds only support a single architecture in CIBW_ARCHS."
        exit 1
    fi

    # Build macOS dependencies in `build/darwin`
    # Install them into `build/deps/darwin`
    WORKDIR=$(pwd)/build/darwin
    BUILD_PREFIX=$(pwd)/build/deps/darwin
else
    # Build prefix will default to /usr/local
    WORKDIR=$(pwd)/build
    MB_ML_LIBC=${AUDITWHEEL_POLICY::9}
    MB_ML_VER=${AUDITWHEEL_POLICY:9}
fi
PLAT=$CIBW_ARCHS

# Define custom utilities
source wheels/multibuild/common_utils.sh
source wheels/multibuild/library_builders.sh
if [ -z "$IS_MACOS" ]; then
    source wheels/multibuild/manylinux_utils.sh
fi

ARCHIVE_SDIR=pillow-depends-main

# Package versions for fresh source builds
ZLIB_NG_VERSION=2.2.4

function build_zlib_ng {
    if [ -e zlib-stamp ]; then return; fi
    git clone https://github.com/radarhere/zlib-ng
    echo "torchstart"
    (cd zlib-ng \
        && git checkout develop \
        && cmake -DZLIB_COMPAT=ON . \
        && cmake --build . --config Release \
        && ctest --verbose -C Release \
        && cmake --build . --target install)
    echo "torchdone"

    if [ -n "$IS_MACOS" ]; then
        # Ensure that on macOS, the library name is an absolute path, not an
        # @rpath, so that delocate picks up the right library (and doesn't need
        # DYLD_LIBRARY_PATH to be set). The default Makefile doesn't have an
        # option to control the install_name.
        install_name_tool -id $BUILD_PREFIX/lib/libz.1.dylib $BUILD_PREFIX/lib/libz.1.dylib
    fi
    touch zlib-stamp
}

function build {
    if [ -z "$IS_ALPINE" ] && [ -z "$SANITIZER" ] && [ -z "$IS_MACOS" ]; then
        yum remove -y zlib-devel
    fi
    build_zlib_ng
}

# Perform all dependency builds in the build subfolder.
mkdir -p $WORKDIR
pushd $WORKDIR > /dev/null

# Any stuff that you need to do before you start building the wheels
# Runs in the root directory of this repository.
if [[ ! -d $WORKDIR/pillow-depends-main ]]; then
  if [[ ! -f $PROJECTDIR/pillow-depends-main.zip ]]; then
    echo "Download pillow dependency sources..."
    curl -fSL -o $PROJECTDIR/pillow-depends-main.zip https://github.com/python-pillow/pillow-depends/archive/main.zip
  fi
  echo "Unpacking pillow dependency sources..."
  untar $PROJECTDIR/pillow-depends-main.zip
fi

if [[ -n "$IS_MACOS" ]]; then
    # Homebrew (or similar packaging environments) install can contain some of
    # the libraries that we're going to build. However, they may be compiled
    # with a MACOSX_DEPLOYMENT_TARGET that doesn't match what we want to use,
    # and they may bring in other dependencies that we don't want. The same will
    # be true of any other locations on the path. To avoid conflicts, strip the
    # path down to the bare minimum (which, on macOS, won't include any
    # development dependencies).
    export PATH="$BUILD_PREFIX/bin:$(dirname $(which python3)):/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin"
    export CMAKE_PREFIX_PATH=$BUILD_PREFIX

    # Ensure the basic structure of the build prefix directory exists.
    mkdir -p "$BUILD_PREFIX/bin"
    mkdir -p "$BUILD_PREFIX/lib"

    # Ensure cmake is available
    python3 -m pip install cmake
fi

wrap_wheel_builder build

# Return to the project root to finish the build
popd > /dev/null
