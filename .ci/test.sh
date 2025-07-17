#!/bin/bash

set -e

python3 -c "from PIL import Image;im = Image.open('test.tif');im.load()"
