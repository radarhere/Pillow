#!/bin/sh

mkdir /var/cache/pacman/pkg
echo "FIRST"
curl -O http://repo.msys2.org/msys/x86_64/msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz
echo "FIRST2"
curl -O http://repo.msys2.org/msys/x86_64/msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz.sig
echo "FIRST3"
pacman -U --noconfirm --ask 20 msys2-keyring-r21.b39fb11-1-any.pkg.tar.xz
echo "FIRST4"
pacman -Syu --noconfirm
echo "FIRST5"
