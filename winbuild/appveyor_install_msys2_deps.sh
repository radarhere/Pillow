#!/bin/sh

mkdir /var/cache/pacman/pkg
pacman -S --noconfirm mingw32/mingw-w64-i686-python3-pip \
     mingw-w64-i686-libjpeg-turbo \

C:/msys64/mingw32/bin/python3 -m pip install --upgrade pip

/mingw32/bin/pip3 install setuptools
