#!/bin/bash

set -e

brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
brew install libpng automake libtool jpeg-turbo

git clone https://github.com/freetype/freetype.git
cd freetype
git checkout sed
sh autogen.sh
./configure --with-harfbuzz=no --with-png=yes && sudo make install

cd ..
make clean
make install
python3 -m PIL.report
python3 demo.py
