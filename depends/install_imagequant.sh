#!/bin/bash
# install libimagequant

echo "0"
archive=freetype-2.8.1

echo "a"
./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz
echo "b"
pushd $archive
echo "c"
./configure
echo "d"
make
echo "e"
sudo make install
echo "f"

popd
