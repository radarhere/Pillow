#!/bin/bash

set -e

python3 -c "from PIL import Image;img = Image.open('image.png');img.load();print(img)"
