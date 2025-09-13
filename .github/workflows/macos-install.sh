#!/bin/bash

set -e

brew update
if [[ "$ImageOS" == "macos13" ]]; then
    brew uninstall gradle maven
fi
brew install \
    jpeg-turbo \
    libimagequant \
    libpng \
    libtiff \
    little-cms2 \
    webp
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

if [[ $GHA_PYTHON_VERSION == "3.11" ]]; then
  brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
  brew install automake libtool
  git clone https://github.com/freetype/freetype.git
  cd freetype

  git checkout VER-2-9-1
  sh autogen.sh
  ./configure --with-harfbuzz=no --with-png=yes && sudo make install
  cd ..
elif [[ $GHA_PYTHON_VERSION == "3.12" ]]; then
  brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
  brew install automake libtool
  git clone https://github.com/freetype/freetype.git
  cd freetype

  git checkout VER-2-10-0
  sh autogen.sh
  ./configure --with-harfbuzz=no --with-png=yes && sudo make install
  cd ..
else
  brew install libraqm
fi

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
