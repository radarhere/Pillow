#!/bin/bash

set -e

brew uninstall freetype ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
brew install libpng automake libtool jpeg-turbo

git clone https://github.com/freetype/freetype.git
cd freetype

echo "Log: 2.13.3 will pass"
git checkout VER-2-13-3
sh autogen.sh
./configure --with-harfbuzz=no --with-png=yes && sudo make install

cd ..
make clean
make install
python3 -m PIL.report
python3 demo.py

cd freetype
echo "Log: The last passing commit"
git checkout VER-2-14-0
git reset --hard HEAD~172

sh autogen.sh
./configure --with-harfbuzz=no --with-png=yes && sudo make install

cd ..
make clean
make install
python3 -m PIL.report
python3 demo.py

cd freetype
if [[ $VERSION == "master" ]]; then
  echo "Log: Master fails"
  git checkout master
else
  echo "Log: The first failing commit"
  git checkout VER-2-14-0
  git reset --hard HEAD~171
  git show
fi
sh autogen.sh
./configure --with-harfbuzz=no --with-png=yes && sudo make install

cd ..
make clean
make install
python3 -m PIL.report
python3 demo.py
