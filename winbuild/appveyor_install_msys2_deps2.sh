#!/bin/sh

echo "FIRST5"
pacman -Sy --noconfirm \
     mingw32/mingw-w64-i686-python-setuptools \
     mingw-w64-i686-libjpeg-turbo \
     mingw-w64-i686-libimagequant
