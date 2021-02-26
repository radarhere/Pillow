#!/bin/bash
# install libimagequant

archive=libimagequant-2.14.0

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

./configure --with-openmp
make clean && make shared
make shared
sudo cp libimagequant.so* /usr/lib/
sudo cp libimagequant.h /usr/include/

popd
