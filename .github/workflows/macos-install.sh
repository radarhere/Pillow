#!/bin/bash

set -e

if [[ "$ImageOS" == "macos13" ]]; then
    brew uninstall gradle maven
fi
brew install \
    zlib-ng libpng
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

git clone https://github.com/mozilla/mozjpeg.git
(cd mozjpeg \
    && git checkout v4.1.1 \
    && mkdir build \
    && cd build \
    && sudo cmake -G"Unix Makefiles" ../ \
    && sudo make install)

python3 -m pip install coverage
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
