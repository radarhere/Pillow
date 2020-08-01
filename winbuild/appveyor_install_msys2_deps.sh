#!/bin/sh

mkdir /var/cache/pacman/pkg
echo "FIRST"
curl -O http://repo.msys2.org/msys/x86_64/msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz
echo "FIRST2"
curl -O http://repo.msys2.org/msys/x86_64/msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz.sig
echo "FIRST3"
pacman -U --noconfirm msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz
echo "FIRST4"
pacman -Syu --noconfirm
echo "FIRST5"
pacman -Syu --noconfirm mingw32/mingw-w64-i686-python3-pip \
     mingw32/mingw-w64-i686-python3-setuptools \
     mingw32/mingw-w64-i686-python3-pytest \
     mingw32/mingw-w64-i686-python3-pytest-cov \
     mingw-w64-i686-libjpeg-turbo \
     mingw-w64-i686-libimagequant

C:/msys64/mingw32/bin/python3 -m pip install --upgrade pip

/mingw32/bin/pip install olefile
/mingw32/bin/pip3 install olefile
