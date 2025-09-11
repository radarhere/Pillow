#!/bin/bash

set -e

brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
brew install libpng
cd winbuild/depends/freetype-2.14.0 && ./configure --with-png=yes && sudo make install
brew install jpeg-turbo
