#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest --require-gil-disabled -s -v -x -W always --cov PIL --cov Tests --cov-report term --cov-report xml Tests/test_core_resources.py $REVERSE
