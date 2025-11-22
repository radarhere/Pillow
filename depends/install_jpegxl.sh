#!/bin/bash

./download-and-extract.sh libjxl-0.8.4 https://github.com/libjxl/libjxl/archive/refs/tags/v0.8.4.tar.gz

pushd libjxl-0.8.4

echo "torch1"
./deps.sh
sudo ldconfig
echo "torch2"

mkdir build
cd build
export CMAKE_INSTALL_PREFIX=/usr/local
export CMAKE_INSTALL_RPATH=/usr/local/lib
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DJPEGXL_ENABLE_SKCMS=OFF -DJPEGXL_ENABLE_SJPEG=OFF -DJPEGXL_ENABLE_PLUGINS=OFF ..
echo "torch3"
../deps.sh
echo "torch4"
cmake --build . -- -j4

sudo cmake --install .

popd

sudo ldconfig
