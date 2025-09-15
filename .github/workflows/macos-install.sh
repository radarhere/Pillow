#!/bin/bash

set -e

brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
HOMEBREW_NO_INSTALL_FROM_API=1 brew install --build-from-source radarhere/homebrew-freetypetap/freetype
brew test freetype
brew audit --strict freetype
brew style freetype
brew install libpng automake libtool jpeg-turbo

make clean
make install
python3 -m PIL.report
python3 demo.py
